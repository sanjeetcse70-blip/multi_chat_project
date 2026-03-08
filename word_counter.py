'''
Docstring for word_counter
Create a program, that asks user to enter a paragraph of text.
Program should do this:
Normalize: lowercase, remove punctuation (.,!?) and extra spaces
Count total number of words
Print Top 5 most frequent words with their counts
Ignore common stop words (like "the", "is", "in", etc.)
'''

def normalize_text(text):
    import string
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = ' '.join(text.split())
    return text

def count_words(text):
    count_dict = {}
    words = text.split()

    stop_words = set(["the", "is", "in", "and", "to", "a", "of", "that", "it", "on", "for", "with", 
                      "as", "was", "at", "by", "an", "be", "this", "from", "or", "which", "but", "not", 
                      "are", "have", "has"])
    
    for word in words:
        if word not in stop_words:
            count_dict[word] = count_dict.get(word, 0) + 1
    return count_dict

def get_top_n_words(count_dict, n=5):
    sorted_words = sorted(count_dict.items(), key=lambda item: item[1], reverse=True)
    return sorted_words[:n]

if __name__ == "__main__":
    paragraph = input("Enter a paragraph of text: ")
    normalized_text = normalize_text(paragraph)
    word_count_dict = count_words(normalized_text)
    total_words = sum(word_count_dict.values())
    
    print(f"\nTotal number of words (excluding stop words): {total_words}")
    
    top_words = get_top_n_words(word_count_dict, 5)
    print("\nTop 5 most frequent words:")
    for word, count in top_words:
        print(f"{word}: {count}")