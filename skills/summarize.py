def run(text):
    words = text.split()

    return {
        "word_count": len(words),
        "preview": " ".join(words[:20])
    }