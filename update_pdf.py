import pymupdf


def add_sequential_page_numbers(
    input_pdf_path, output_pdf_path, start_pdf_page, total_pages, start_page_num
):
    doc = pymupdf.open(input_pdf_path)

    start_idx = start_pdf_page - 1
    end_idx = start_idx + total_pages

    for idx in range(start_idx, end_idx):
        if idx >= len(doc):
            break

        page = doc[idx]
        page_width = page.rect.width
        page_height = page.rect.height

        current_page_num = start_page_num + (idx - start_idx)

        x_center = page_width / 2
        y_bottom = page_height - 36

        # Mask existing number area and insert updated number
        white_box = pymupdf.Rect(
            x_center - 30, y_bottom - 12, x_center + 30, y_bottom + 10
        )
        page.draw_rect(white_box, color=(1, 1, 1), fill=(1, 1, 1))
        page.insert_text(
            pymupdf.Point(x_center - 8, y_bottom),
            str(current_page_num),
            fontsize=11,
            fontname="helv",
            color=(0, 0, 0),
        )

    # Clean save with stream compression
    doc.save(output_pdf_path, deflate=True)
    doc.close()
    print(f"Successfully updated PDF saved to: {output_pdf_path}")


# Execute with paths relative to Modelling_report folder.
# Always overwrite the same live PDF in build/main.pdf.
add_sequential_page_numbers(
    input_pdf_path="build/main.pdf",
    output_pdf_path="build/main.pdf",
    start_pdf_page=120,
    total_pages=18,
    start_page_num=120,
)