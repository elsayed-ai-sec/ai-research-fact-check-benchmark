import verify_sources


def test_normalize_ignores_case_and_extra_whitespace():
    assert verify_sources.normalize("  AI   Risk Framework ") == \
           verify_sources.normalize("ai risk framework")


def test_text_extractor_reads_page_text():
    parser = verify_sources.TextExtractor()
    parser.feed(
        "<html><body><p>January 26, 2023</p>"
        "<script>fake hidden text</script></body></html>"
    )
    text = verify_sources.normalize(" ".join(parser.parts))
    assert "january 26, 2023" in text
    assert "fake hidden text" not in text


def test_source_match_and_no_match_labels_are_distinct():
    expected = verify_sources.normalize("January 26, 2023")
    page_with_answer = verify_sources.normalize(
        "The framework was published January 26, 2023."
    )
    page_without_answer = verify_sources.normalize(
        "The framework was published in 2023."
    )

    assert expected in page_with_answer
    assert expected not in page_without_answer
