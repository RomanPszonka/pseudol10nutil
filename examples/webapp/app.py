#!/usr/bin/env python3

from flask import Flask, jsonify, make_response, redirect, render_template, request, send_file
import os
import tempfile

import pseudol10nutil.transforms as xforms
from pseudol10nutil import PseudoL10nUtil, POFileUtil

app = Flask(__name__)
appname = "pseudol10nutil"
api_version = "v1.0"
api_base_url = "/{0}/api/{1}/".format(appname, api_version)
ui_base_url = "/{0}/".format(appname)
util = PseudoL10nUtil()


@app.errorhandler(404)
def handle_404(error):
    if (
        request.accept_mimetypes.best_match(["application/json", "text/html"])
        == "application/json"
    ):
        return make_response(
            jsonify(
                {
                    "error": "404 Error: URL not found.  Please check your spelling and try again."
                }
            ),
            404,
        )
    else:
        return render_template("404.html"), 404


@app.route(api_base_url + "pseudo", methods=["POST"])
def do_pseudo():
    if "strings" in request.get_json():
        data = request.json["strings"]
    else:
        return make_response(
            jsonify({"error": "400 Error: Could not process request."}), 400
        )
    for k, v in data.items():
        data[k] = util.pseudolocalize(v)
    result = {"strings": data}
    return jsonify(result)


@app.route("/")
def home():
    return redirect(ui_base_url)


@app.route(ui_base_url, methods=["GET", "POST"])
def do_pseudo_ui():
    if request.method == "POST":
        input_text = request.form.get("pseudolocalize_input")
        substitute = request.form.get("substitution_type")
        brackets = request.form.get("add_brackets")
        pad_length = True if "pad_length" in request.form else False

        transforms = []
        form_options = {}  # Preserve options on post back

        if substitute == "diacritics":
            transforms.append(xforms.transliterate_diacritic)
            form_options["sub_diacritics"] = "checked"
        elif substitute == "fullwidth":
            transforms.append(xforms.transliterate_fullwidth)
            form_options["sub_fullwidth"] = "checked"
        elif substitute == "circled":
            transforms.append(xforms.transliterate_circled)
            form_options["sub_circled"] = "checked"
        else:
            form_options["sub_none"] = "checked"

        if pad_length:
            transforms.append(xforms.pad_length)
            form_options["do_pad_length"] = "checked"

        if brackets == "square":
            transforms.append(xforms.square_brackets)
            form_options["brackets_square"] = "checked"
        elif brackets == "angle":
            transforms.append(xforms.angle_brackets)
            form_options["brackets_angle"] = "checked"
        elif brackets == "curly":
            transforms.append(xforms.curly_brackets)
            form_options["brackets_curly"] = "checked"
        else:
            form_options["brackets_none"] = "checked"

        util.transforms = transforms
        pseudolocalized_text_output = util.pseudolocalize(input_text)
        return render_template(
            "pseudolocalize_template.html",
            pseudolocalized_text_input=input_text,
            pseudolocalized_text_output=pseudolocalized_text_output,
            **form_options,
        )
    else:
        default_options = {
            "sub_diacritics": "checked",
            "brackets_square": "checked",
            "do_pad_length": "checked",
        }
        return render_template("pseudolocalize_template.html", **default_options)


@app.route(ui_base_url + "po_upload", methods=["POST"])
def do_pseudo_po_upload():
    input_temp_file_path = None
    output_temp_file_path = None
    try:
        if "po_file" not in request.files:
            return make_response(
                jsonify({"error": "400 Error: No file part in the request."}), 400
            )

        file = request.files["po_file"]

        if file.filename == "":
            return make_response(
                jsonify({"error": "400 Error: No file selected for uploading."}), 400
            )

        if not file.filename.endswith(".po"):
            return make_response(
                jsonify(
                    {"error": "400 Error: Invalid file type. Please upload a .po file."}
                ),
                400,
            )

        # Create temporary files
        fd_input, input_temp_file_path = tempfile.mkstemp(suffix=".po")
        os.close(fd_input) # close file descriptor as pofileutil will open and close the file
        fd_output, output_temp_file_path = tempfile.mkstemp(suffix=".po")
        os.close(fd_output) # close file descriptor as pofileutil will open and close the file


        file.save(input_temp_file_path)

        pofileutil = POFileUtil()
        # Apply the same transforms as the UI text input for consistency
        # Default to diacritics, square brackets, and padding
        # This could be made configurable in the UI later if needed
        current_transforms = [
            xforms.transliterate_diacritic,
            xforms.pad_length,
            xforms.square_brackets
        ]
        pofileutil.transforms = current_transforms
        pofileutil.pseudolocalizefile(input_temp_file_path, output_temp_file_path)

        return send_file(
            output_temp_file_path,
            as_attachment=True,
            download_name="pseudolocalized.po",
            mimetype="application/x-po",
        )
    except Exception as e:
        # Log the exception e for debugging if necessary
        return make_response(
            jsonify({"error": f"500 Error: Internal server error during processing. {str(e)}"}), 500
        )
    finally:
        if input_temp_file_path and os.path.exists(input_temp_file_path):
            os.remove(input_temp_file_path)
        if output_temp_file_path and os.path.exists(output_temp_file_path):
            os.remove(output_temp_file_path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
