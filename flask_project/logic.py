def run_layoutlm_on_pdf(pdf_path, output_dir):
    from layout_lm_tutorial import layoutlm_preprocess
    from torch.nn import CrossEntropyLoss
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image, ImageDraw, ImageFont
    from IPython.display import display
    from io import BytesIO
    import os

    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    model_path='./models/layoutlm1.pt'

    def get_labels(path):
        with open(path, "r") as f:
            labels = f.read().splitlines()
        if "O" not in labels:
            labels = ["O"] + labels
        return labels

    labels = get_labels("./labels.txt")
    num_labels = len(labels)
    model=layoutlm_preprocess.model_load(model_path,num_labels)

    label_map = {i: label for i, label in enumerate(labels)}
    # Use cross entropy ignore index as padding label id so that only real label ids contribute to the loss later
    pad_token_label_id = CrossEntropyLoss().ignore_index

    test_pdf = pdf_path

    images = convert_from_path(test_pdf, 500, poppler_path=r'C:\Program Files\poppler-24.08.0\Library\bin')
    image_paths = []

    for i,img in enumerate(images):
        image_main = img.convert("RGB")
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        image, words, boxes, actual_boxes = layoutlm_preprocess.preprocess(img_io)
        word_level_predictions, final_boxes=layoutlm_preprocess.convert_to_features(image, words, boxes, actual_boxes, model)

        draw = ImageDraw.Draw(image)
        #font = ImageFont.load_default()
        font_path = "C:/Windows/Fonts/arial.ttf"
        font = ImageFont.truetype(font_path, size=50)
        def iob_to_label(label):
            if label != 'O':
                return label[2:]
            else:
                return "other"
        label2color = {'question':'blue', 'answer':'green', 'header':'orange', 'other':'violet'}
        for prediction, box in zip(word_level_predictions, final_boxes):
            predicted_label = iob_to_label(label_map[prediction]).lower()
            draw.rectangle(box, outline=label2color[predicted_label])
            draw.text((box[0] + 10, box[1] - 10), text=predicted_label, fill=label2color[predicted_label], font=font)
        #img_save_path= f'./static/results/output_page_{i}.png'
        img_save_path = os.path.join(output_dir, f"output_page_{i}.png")
        image.save(img_save_path)
        image_paths.append(img_save_path)


    return image_paths
