// CS417 AI Project - Wang Hao Automated Theorem Prover
let examplesList = [];
let currentResult = null;
let stepIndex = 0;
let stepNodesList = [];

document.addEventListener("DOMContentLoaded", () => {
    loadExamples();
});

// 1. Tải danh sách bài toán mẫu từ API
async function loadExamples() {
    try {
        const res = await fetch("/api/examples");
        const data = await res.json();
        if (data.success) {
            examplesList = data.examples;
            const select = document.getElementById("exampleSelect");
            examplesList.forEach((ex, idx) => {
                const opt = document.createElement("option");
                opt.value = ex.id;
                const tag = ex.category === "real_life" ? "⭐ [Thực tế]" : "📖 [Kinh điển]";
                opt.textContent = `${tag} ${ex.name}`;
                select.appendChild(opt);
            });

            // Mặc định chọn bài toán ĐH Duy Tân đầu tiên
            if (examplesList.length > 0) {
                select.value = examplesList[0].id;
                onSelectExample();
            }
        }
    } catch (err) {
        console.error("Lỗi khi tải thư viện bài toán:", err);
    }
}

// 2. Khi người dùng chọn một bài toán mẫu
function onSelectExample() {
    const select = document.getElementById("exampleSelect");
    const id = select.value;
    if (!id) return;

    const item = examplesList.find(e => e.id === id);
    if (!item) return;

    document.getElementById("sequentInput").value = item.sequent;

    const natBox = document.getElementById("naturalLanguageBox");
    const natText = document.getElementById("naturalText");
    const varBox = document.getElementById("variableMappings");

    if (item.natural_language) {
        natBox.style.display = "block";
        natText.textContent = item.natural_language;

        varBox.innerHTML = "";
        if (item.variables) {
            for (let v in item.variables) {
                const div = document.createElement("div");
                div.className = "var-item";
                div.innerHTML = `<span class="var-badge">${v}</span>: "${item.variables[v]}"`;
                varBox.appendChild(div);
            }
        }
    } else {
        natBox.style.display = "none";
    }
}

// 3. Chèn ký hiệu từ bàn phím ảo
function insertSymbol(sym) {
    const input = document.getElementById("sequentInput");
    const start = input.selectionStart;
    const end = input.selectionEnd;
    const text = input.value;
    input.value = text.substring(0, start) + sym + text.substring(end);
    input.focus();
    input.selectionStart = input.selectionEnd = start + sym.length;
}

// 4. Chạy giải thuật Vương Hạo
async function runProver() {
    const input = document.getElementById("sequentInput").value.trim();
    if (!input) {
        alert("Vui lòng nhập công thức logic cần chứng minh!");
        return;
    }

    const select = document.getElementById("exampleSelect");
    const currentExample = examplesList.find(e => e.id === select.value);
    const variables = currentExample ? currentExample.variables : {};

    const btn = document.getElementById("proveBtn");
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang chứng minh...';

    try {
        const res = await fetch("/api/prove", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                sequent: input,
                variables: variables
            })
        });

        const data = await res.json();
        if (!data.success) {
            alert(data.error);
            return;
        }

        currentResult = data;
        renderProofResults(data);

    } catch (err) {
        console.error(err);
        alert("Lỗi khi kết nối với máy chủ chứng minh!");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> CHỨNG MINH ĐỊNH LÝ';
    }
}

// 5. Hiển thị kết quả lên giao diện
function renderProofResults(data) {
    const banner = document.getElementById("resultBanner");
    const bannerTitle = document.getElementById("bannerTitle");
    const bannerSubtitle = document.getElementById("bannerSubtitle");
    const bannerIcon = document.getElementById("bannerIcon");
    const bannerStats = document.getElementById("bannerStats");

    bannerStats.style.display = "flex";
    document.getElementById("statNodes").textContent = data.total_nodes;
    document.getElementById("statAxioms").textContent = data.proven_branches;
    document.getElementById("statLeaves").textContent = data.total_leaves;

    if (data.is_valid) {
        banner.className = "card result-banner-card proven";
        bannerIcon.innerHTML = '<i class="fa-solid fa-circle-check"></i>';
        bannerTitle.textContent = "ĐỊNH LÝ ĐÃ ĐƯỢC CHỨNG MINH THÀNH CÔNG (HẰNG ĐÚNG)!";
        bannerSubtitle.textContent = `Tất cả ${data.proven_branches} / ${data.total_leaves} nhánh đều được quy về Tiên đề (Axiom). Biểu thức luôn đúng trong mọi trường hợp chân trị.`;
        document.getElementById("counterCard").style.display = "none";
    } else {
        banner.className = "card result-banner-card invalid";
        bannerIcon.innerHTML = '<i class="fa-solid fa-circle-xmark"></i>';
        bannerTitle.textContent = "KHÔNG PHẢI HẰNG ĐÚNG (CHỨNG MINH THẤT BẠI)!";
        bannerSubtitle.textContent = `Phát hiện ${data.total_leaves - data.proven_branches} nhánh bế tắc không thể đưa về Tiên đề. Tồn tại ít nhất một trường hợp làm sai định lý.`;
        
        // Hiển thị phản ví dụ
        renderCounterExample(data.counter_example_analysis, data.variables);
    }

    // Vẽ Cây Chứng Minh Trực Quan
    renderProofTree(data.proof_tree);

    // Hiển thị Tiến trình từng bước
    renderTraceLog(data.text_trace);
}

// 6. Hiển thị Phản ví dụ (Counter-Model)
function renderCounterExample(analysis, variables) {
    const card = document.getElementById("counterCard");
    const body = document.getElementById("counterBody");
    if (!analysis) {
        card.style.display = "none";
        return;
    }

    card.style.display = "block";
    let assignHtml = '<div class="counter-assign-box">';
    for (let varName in analysis.assignment) {
        const boolVal = analysis.assignment[varName];
        const valText = boolVal ? '<b style="color:#15803d;">TRUE (1)</b>' : '<b style="color:#b91c1c;">FALSE (0)</b>';
        const meaning = variables && variables[varName] ? ` <span style="color:#64748b; font-size:0.75rem;">(${variables[varName]})</span>` : '';
        assignHtml += `<div class="assign-item">${varName} = ${valText}${meaning}</div>`;
    }
    assignHtml += '</div>';

    let detailsHtml = `
        <div><strong>Nguyên nhân thất bại:</strong> ${analysis.explanation}</div>
        <div style="margin-top: 0.4rem; font-size: 0.82rem; color: #475569;">
            Khi thay bộ giá trị chân trị trên vào bài toán: Tất cả các Tiền đề đều nhận giá trị <b>Đúng</b>, nhưng Kết luận lại nhận giá trị <b>Sai</b>. 
            Do đó quan hệ suy kéo <i>(Tiền đề ⟹ Kết luận)</i> bị vi phạm!
        </div>
    `;

    body.innerHTML = assignHtml + detailsHtml;
}

// 7. Vẽ Cây dẫn xuất trực quan (Visual Proof Tree)
function renderProofTree(rootNode) {
    const container = document.getElementById("treeContainer");
    container.innerHTML = "";

    const treeWrapper = document.createElement("div");
    treeWrapper.className = "tree-node-wrapper";

    function buildNodeHtml(node) {
        const divWrapper = document.createElement("div");
        divWrapper.className = "tree-node-wrapper";

        const nodeBox = document.createElement("div");
        let statusClass = "node-expanded";
        if (node.status === "PROVEN_AXIOM") statusClass = "node-axiom";
        if (node.status === "INVALID") statusClass = "node-invalid";

        nodeBox.className = `tree-node ${statusClass}`;
        
        let statusBadge = "";
        if (node.status === "PROVEN_AXIOM") {
            statusBadge = `<div class="node-axiom-badge"><i class="fa-solid fa-check"></i> TIÊN ĐỀ HỢP LỆ (Trùng '${node.axiom_formula}')</div>`;
        } else if (node.status === "INVALID") {
            statusBadge = `<div class="node-invalid-badge"><i class="fa-solid fa-xmark"></i> BẾ TẮC (Khác nhau: ${JSON.stringify(node.counter_example)})</div>`;
        }

        nodeBox.innerHTML = `
            <div class="node-header">
                <span>Nút #${node.node_id} (Độ sâu ${node.depth})</span>
                <span>${node.status}</span>
            </div>
            <div class="node-sequent">${escapeHtml(node.sequent_str)}</div>
            ${node.rule_applied ? `<div class="node-rule">${escapeHtml(node.rule_applied)}</div>` : ''}
            ${statusBadge}
        `;

        divWrapper.appendChild(nodeBox);

        // Nếu có các nhánh con
        if (node.children && node.children.length > 0) {
            const line = document.createElement("div");
            line.className = "tree-branch-line";
            divWrapper.appendChild(line);

            const childrenBox = document.createElement("div");
            childrenBox.className = "tree-children";

            node.children.forEach(child => {
                childrenBox.appendChild(buildNodeHtml(child));
            });

            divWrapper.appendChild(childrenBox);
        }

        return divWrapper;
    }

    treeWrapper.appendChild(buildNodeHtml(rootNode));
    container.appendChild(treeWrapper);
}

// 8. Hiển thị Tiến trình từng bước dạng văn bản
function renderTraceLog(traceLines) {
    const logBox = document.getElementById("traceLog");
    logBox.innerHTML = "";

    if (!traceLines || traceLines.length === 0) {
        logBox.innerHTML = `<div class="text-center text-muted">Chưa có dữ liệu tiến trình.</div>`;
        return;
    }

    traceLines.forEach(line => {
        const div = document.createElement("div");
        if (line.includes("[✓ TIÊN ĐỀ")) {
            div.className = "trace-line-axiom";
        } else if (line.includes("[✗ BẾ TẮC")) {
            div.className = "trace-line-invalid";
        } else if (line.trim().startsWith("↳")) {
            div.className = "trace-line-rule";
        }
        div.textContent = line;
        logBox.appendChild(div);
    });
}

// 9. Mô phỏng từng bước (Step-by-step)
function startStepByStep() {
    runProver();
    // Cuộn mượt xuống cây chứng minh
    document.getElementById("treeContainer").scrollIntoView({ behavior: 'smooth' });
}

// 10. Mở rộng tất cả các nút
function expandAllNodes() {
    const container = document.getElementById("treeContainer");
    container.scrollLeft = 0;
}

// 11. Sao chép LaTeX Sequent
function exportLaTeX() {
    if (!currentResult || !currentResult.root_latex) {
        alert("Chưa có dữ liệu chứng minh để xuất LaTeX!");
        return;
    }
    const latex = `\\vdash ${currentResult.root_latex}`;
    navigator.clipboard.writeText(latex).then(() => {
        alert("Đã sao chép biểu thức LaTeX vào bộ nhớ tạm:\n" + latex);
    });
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
