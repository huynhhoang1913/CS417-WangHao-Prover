import sys
import os
import json

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from flask import Flask, render_template, jsonify, request

from core.parser import LogicParser
from core.wang_hao import WangHaoProver
from core.counter_example import CounterExampleVerifier

app = Flask(__name__)

LIB_PATH = os.path.join(os.path.dirname(__file__), "examples", "problem_library.json")
with open(LIB_PATH, "r", encoding="utf-8") as f:
    PROBLEM_LIBRARY = json.load(f)

parser = LogicParser()
prover = WangHaoProver()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/examples", methods=["GET"])
def get_examples():
    return jsonify({
        "success": True,
        "count": len(PROBLEM_LIBRARY),
        "examples": PROBLEM_LIBRARY
    })

@app.route("/api/prove", methods=["POST"])
def prove_sequent():
    data = request.get_json() or {}
    sequent_str = data.get("sequent", "").strip()
    variables = data.get("variables", {})

    if not sequent_str:
        return jsonify({"success": False, "error": "Vui lòng nhập công thức logic cần chứng minh!"}), 400

    try:
        gamma, delta = parser.parse_sequent(sequent_str)
    except Exception as e:
        return jsonify({"success": False, "error": f"Lỗi cú pháp: {str(e)}"}), 400

    # Thực thi giải thuật Vương Hạo
    result = prover.prove(gamma, delta)

    # Nếu có phản ví dụ, tiến hành phân tích và kiểm chứng
    counter_example_analysis = None
    if not result["is_valid"] and result["counter_examples"]:
        ce = result["counter_examples"][0]
        counter_example_analysis = CounterExampleVerifier.verify_counter_example(gamma, delta, ce)

    # Chuyển đổi các biến để hiển thị
    all_atoms = set()
    for f in gamma + delta:
        all_atoms.update(f.get_atoms())

    return jsonify({
        "success": True,
        "sequent_input": sequent_str,
        "gamma_str": [f.to_str() for f in gamma],
        "delta_str": [f.to_str() for f in delta],
        "is_valid": result["is_valid"],
        "total_nodes": result["total_nodes"],
        "total_leaves": result["total_leaves"],
        "proven_branches": result["proven_branches"],
        "counter_examples": result["counter_examples"],
        "counter_example_analysis": counter_example_analysis,
        "proof_tree": result["proof_tree"],
        "text_trace": result["text_trace"],
        "root_latex": result["root_latex"],
        "atoms": list(all_atoms),
        "variables": variables
    })

if __name__ == "__main__":
    print("🚀 Đang khởi chạy Hệ thống Chứng minh Định lý Vương Hạo (CS417 - ĐH Duy Tân)...")
    print("👉 Mở trình duyệt tại: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
