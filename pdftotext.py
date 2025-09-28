import fitz
import csv
import re

def parse_vocabulary_text(text):
    """텍스트에서 단어, 의미, 예문을 추출하는 함수"""
    result = {
        'english_word': None,
        'korean_meaning': None,
        'example_sentence': None,
        'choices': None,
        'interpretation': None
    }

    # 번호와 영어 단어 추출 (예: "601. prior:")
    word_pattern = r'(\d+)\.\s*([^:;]+):'
    word_match = re.search(word_pattern, text)
    if word_match:
        english_word = word_match.group(2).strip()
        # 영어 단어가 실제로 영어인지 확인 (간단한 체크)
        if re.match(r'^[a-zA-Z\s]+$', english_word):
            result['english_word'] = english_word

    # 세미콜론(;) 뒤의 한국어 의미 추출
    meaning_pattern = r';([^<]+)'
    meaning_match = re.search(meaning_pattern, text)
    if meaning_match:
        result['korean_meaning'] = meaning_match.group(1).strip()
    else:
        # 세미콜론이 없고 번호 패턴이 있는 경우만 콜론(:) 뒤의 내용을 의미로 사용
        if word_match:  # 번호 패턴이 있을 때만
            colon_pattern = r':\s*([^<]+)'
            colon_match = re.search(colon_pattern, text)
            if colon_match:
                meaning_text = colon_match.group(1).strip()
                # < 예제> 앞까지만 추출
                if '< 예제>' in meaning_text:
                    meaning_text = meaning_text.split('< 예제>')[0].strip()
                if meaning_text:  # 빈 문자열이 아닌 경우만
                    result['korean_meaning'] = meaning_text

    # < 예제> 뒤의 예문 추출
    example_pattern = r'< 예제>\s*([^{]+)'
    example_match = re.search(example_pattern, text)
    if example_match:
        example_text = example_match.group(1).strip()
        if example_text:  # 빈 문자열이 아닌 경우만
            result['example_sentence'] = example_text

    # 선택지 추출 (예: "(A) Prior(B) Earlier")
    choices_pattern = r'\([A-D]\)[^()]*(?:\([A-D]\)[^()]*)*'
    choices_match = re.search(choices_pattern, text)
    if choices_match:
        result['choices'] = choices_match.group(0).strip()

    # 해석 추출 (예: "{해석}~로의 고용에 앞서")
    interpretation_pattern = r'\{해석\}([^}]*(?:\}[^}]*)*)'
    interpretation_match = re.search(interpretation_pattern, text)
    if interpretation_match:
        interpretation_text = interpretation_match.group(1).strip()
        if interpretation_text:  # 빈 문자열이 아닌 경우만
            result['interpretation'] = interpretation_text

    return result

if __name__ == "__main__":
    doc = fitz.open('test.pdf')

    # CSV 파일로 저장할 데이터 리스트
    vocabulary_data = []

    for i in range(len(doc)):
        page = doc.load_page(i)
        text = page.get_text()

        # 특정 패턴 제거
        text = text.replace(" join the company/our department/the university", "")

        if text.strip():  # 빈 텍스트가 아닌 경우만
            # 텍스트를 줄 단위로 분리해서 각각 파싱
            lines = text.strip().split('\n')
            current_entry = None

            for line in lines:
                line = line.strip()
                if not line or line in ['<1일차>', '<2일차>', '<3일차>', '<4일차>', '<5일차>', '<6일차>', '<7일차>', '<8일차>', '<9일차>', '<10일차>']:
                    continue

                # 번호 패턴 체크 (새로운 단어 시작)
                if re.match(r'\d+\.', line):
                    # 이전 entry가 있다면 저장
                    if current_entry:
                        vocabulary_data.append(current_entry)

                    # 새로운 entry 시작
                    parsed_data = parse_vocabulary_text(line)
                    current_entry = {
                        'page': i + 1,
                        'english_word': parsed_data['english_word'],
                        'korean_meaning': parsed_data['korean_meaning'],
                        'example_sentence': parsed_data['example_sentence'],
                        'choices': parsed_data['choices'],
                        'interpretation': parsed_data['interpretation'],
                        'raw_content': line
                    }
                else:
                    # 기존 entry에 추가 정보가 있는 경우
                    if current_entry:
                        # 예제나 해석 등 추가 정보 처리
                        if '< 예제>' in line and not current_entry['example_sentence']:
                            example_match = re.search(r'< 예제>\s*(.+)', line)
                            if example_match:
                                current_entry['example_sentence'] = example_match.group(1).strip()

                        # 선택지 정보 추가
                        if re.search(r'\([A-D]\)', line) and not current_entry['choices']:
                            choices_match = re.search(r'\([A-D]\)[^()]*(?:\([A-D]\)[^()]*)*', line)
                            if choices_match:
                                current_entry['choices'] = choices_match.group(0).strip()

                        # 해석 정보 추가
                        if '{해석}' in line and not current_entry['interpretation']:
                            interpretation_match = re.search(r'\{해석\}(.+)', line)
                            if interpretation_match:
                                current_entry['interpretation'] = interpretation_match.group(1).strip()

                        # raw_content에 추가
                        current_entry['raw_content'] += '\n' + line

            # 마지막 entry 저장
            if current_entry:
                vocabulary_data.append(current_entry)

        print(text)

    doc.close()

    # CSV 파일로 저장
    with open('vocabulary.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['page', 'english_word', 'korean_meaning', 'example_sentence', 'choices', 'interpretation', 'raw_content']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(vocabulary_data)

    print(f"\nCSV 파일이 생성되었습니다: vocabulary.csv ({len(vocabulary_data)}개 행)")
