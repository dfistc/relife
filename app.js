const state = { papers: [], filter: "all", relevance: "all", dateRange: "all", dateFrom: "", dateTo: "" };

const journalMeta = {
  "Science": { if: "45.8", ifYear: "2024 JIF", cas: "1区 / TOP（建议以最新版复核）", type: "CNS 正刊" },
  "Trends in Molecular Medicine": { if: "13.8", ifYear: "公开期刊指标", cas: "1区 / TOP（建议以最新版复核）", type: "非 CNS · 高水平综述期刊" },
  "Nature Metabolism": { if: "20.8", ifYear: "公开期刊指标", cas: "1区 / TOP（建议以最新版复核）", type: "Nature 子刊" },
  "Cellular & Molecular Biology Letters": { if: "8.3", ifYear: "公开期刊指标", cas: "待中科院升级版数据库核验", type: "非 CNS" },
  "American Journal of Physiology-Endocrinology and Metabolism": { if: "3.1", ifYear: "2024 JIF", cas: "待中科院升级版数据库核验", type: "非 CNS" },
  "Journal of Ovarian Research": { if: "4.4", ifYear: "2024 5-year JIF", cas: "待中科院升级版数据库核验", type: "非 CNS" },
  "Biomolecules": { if: "4.8", ifYear: "公开期刊指标", cas: "待中科院升级版数据库核验", type: "非 CNS" },
  "microPublication Biology": { if: "无 JIF", ifYear: "未检出", cas: "未收录 / 待核验", type: "非 CNS" },
  "medRxiv preprint": { if: "无 IF", ifYear: "预印本", cas: "不适用", type: "预印本 · 非 CNS" }
};

const paperMeta = {
  "38870290": ["原创研究", "PCOS · 卵巢类固醇生成 · 药物靶点", "可借鉴 LONP1-底物互作与蛋白降解机制，设计 PCOS 高雄激素干预及靶点验证实验。"],
  "39648053": ["论坛综述", "卵巢生物学 · PCOS · 卵巢衰老", "适合构建 LONP1 在卵巢中的机制框架，并寻找 PCOS 与卵巢衰老之间的共同线粒体通路。"],
  "PPR863667": ["病例对照研究 · 预印本", "PCOS · BMP8B 生物标志物 · 代谢", "提示可检测循环 BMP8B，并将其与胰岛素抵抗、BMI 和脂代谢指标进行临床相关性分析。"],
  "41696866": ["原创研究", "PCOS · 运动干预 · 线粒体蛋白稳态", "提供运动-LONP1-线粒体蛋白稳态的干预链条，可用于设计 PCOS 运动及组织特异性验证。"],
  "PMC12628819": ["原创研究 · 单细胞转录组", "PCOS · 卵巢膜细胞 · 高雄激素", "AKT-LONP1-STAR 轴可作为单细胞数据分析、膜细胞验证和高雄激素机制研究的直接参考。"],
  "40181907": ["原创研究", "中枢能量稳态 · BMP8B · 性别差异", "提示 BMP8B 的中枢效应存在性别差异，可启发研究下丘脑-交感神经-脂肪产热轴。"],
  "PMC12024584": ["综述", "LONP1 药理学 · 线粒体蛋白稳态", "汇总 LONP1 小分子调节剂，可用于筛选改善 PCOS 线粒体异常或脂肪细胞功能的候选工具化合物。"],
  "41620670": ["综述", "LONP1 · 线粒体稳态 · 疾病机制", "系统梳理 LONP1 的质量控制、代谢和疾病通路，可帮助选择产热或 PCOS 研究中的下游指标与干预节点。"]
  ,"10.1038/s42255-025-01378-8": ["原创研究 · 单细胞与表观组学", "HMGCS2 · 米色脂肪生成 · 产热 · 发育代谢", "直接证明 Hmgcs2 依赖的酮体信号促进米色脂肪形成，可重点借鉴 Hmgcs2 敲除、Cd81+ 前体细胞、组蛋白乙酰化与 β-羟丁酰化实验体系。"]
};

const escapeHtml = (text = "") => String(text ?? "").replace(/[&<>"']/g, c => ({
  "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
}[c]));

const relevanceById = {
  "10.1038/s42255-025-01378-8": "direct",
  "38870290": "direct",
  "PPR863667": "direct",
  "41696866": "direct",
  "PMC12628819": "direct",
  "40181907": "direct",
  "39648053": "direct",
  "40281347": "inspirational",
  "41620670": "inspirational",
  "PMC12024584": "inspirational"
};

function matchesDate(p) {
  if (state.dateRange === "all" && !state.dateFrom && !state.dateTo) return true;
  const added = new Date(`${p.added_date || "2026-06-07"}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (state.dateRange === "today") return added.getTime() === today.getTime();
  if (["7", "30"].includes(state.dateRange)) {
    const start = new Date(today);
    start.setDate(start.getDate() - Number(state.dateRange) + 1);
    return added >= start && added <= today;
  }
  if (state.dateFrom && added < new Date(`${state.dateFrom}T00:00:00`)) return false;
  if (state.dateTo && added > new Date(`${state.dateTo}T23:59:59`)) return false;
  return true;
}

function render() {
  const list = state.papers.filter(p => {
    const mainMatch = state.filter === "all" || (state.filter === "qualified" ? p.qualified : p.genes.includes(state.filter));
    const relevanceMatch = state.relevance === "all" || (p.relevance || relevanceById[p.id]) === state.relevance;
    return mainMatch && relevanceMatch && matchesDate(p);
  });
  document.querySelector("#result-count").textContent = `当前显示 ${list.length} / ${state.papers.length} 篇文献`;
  document.querySelector("#papers").innerHTML = list.map(p => {
    const meta = paperMeta[p.id] || [p.article_type || "研究型文献", p.field || p.topics.join(" / "), p.inspiration || "可用于机制设计、靶点验证或研究背景梳理。"];
    const relevance = p.relevance || relevanceById[p.id] || "inspirational";
    return `
    <article class="paper-card">
      <div class="paper-meta">
        <span class="tag ${relevance}">${relevance === "direct" ? "直接相关" : "启发性相关"}</span>
        <span class="tag">网站更新 ${escapeHtml(p.added_date || "2026-06-07")}</span>
        ${p.genes.map(g => `<span class="tag">${escapeHtml(g)}</span>`).join("")}
        ${p.topics.map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("")}
        <span class="tag ${p.qualified ? "" : "warn"}">${p.qualified ? `IF ${p.impact_factor}` : `IF ${escapeHtml(p.if_status)}`}</span>
      </div>
      <h3>${escapeHtml(p.title)}</h3>
      <p class="citation">${escapeHtml(p.journal)} · ${escapeHtml(p.date)} · ${escapeHtml(p.authors)}</p>
      <div class="journal-facts">
        <span><b>中科院分区</b>${escapeHtml((journalMeta[p.journal] || {}).cas || "待核验")}</span>
        <span><b>IF</b>${escapeHtml((journalMeta[p.journal] || {}).if || p.impact_factor || "待核验")} <small>${escapeHtml((journalMeta[p.journal] || {}).ifYear || "")}</small></span>
        <span><b>期刊类型</b>${escapeHtml((journalMeta[p.journal] || {}).type || "非 CNS / 待核验")}</span>
        <span><b>文章类型</b>${escapeHtml(meta[0])}</span>
        <span><b>所属领域</b>${escapeHtml(meta[1])}</span>
      </div>
      <div class="inspiration"><b>对脂肪产热 / PCOS 研究的启发</b><p>${escapeHtml(meta[2])}</p></div>
      <div class="abstracts">
        <div><h4>中文摘要性概述</h4><p>${escapeHtml(p.summary_zh)}</p></div>
        <div><h4>ENGLISH SUMMARY</h4><p>${escapeHtml(p.summary_en)}</p></div>
      </div>
      <div class="paper-links">
        <a class="paper-link" href="${encodeURI(p.url)}" target="_blank" rel="noopener">原文直达 / Publisher ↗</a>
        ${p.source_url ? `<a class="paper-link secondary" href="${encodeURI(p.source_url)}" target="_blank" rel="noopener">PubMed / PMC 核验 ↗</a>` : ""}
        <a class="paper-link method-download" href="downloads/${encodeURIComponent(String(p.id).replaceAll("/", "_"))}-methods.pdf" download>下载实验路线与方法 PDF ↓</a>
      </div>
    </article>
  `}).join("");
  document.querySelector("#empty-qualified").hidden = !(state.filter === "qualified" && list.length === 0);
}

fetch(`data/papers.json?v=${Date.now()}`, { cache: "no-store" })
  .then(r => r.json())
  .then(data => {
    state.papers = data.papers;
    document.querySelector("#last-updated").textContent = `上次检索：${data.last_checked}（Asia/Shanghai）`;
    document.querySelector("#since-year").textContent = data.criteria.since.slice(0, 4);
    document.querySelector("#qualified-count").textContent = data.papers.filter(p => p.qualified).length;
    document.querySelector("#candidate-count").textContent = data.papers.filter(p => !p.qualified).length;
    const latestAddedDate = data.papers.map(p => p.added_date).filter(Boolean).sort().at(-1) || "--";
    document.querySelector("#latest-update-date").textContent = latestAddedDate;
    document.querySelector("#latest-update-count").textContent = data.papers.filter(p => p.added_date === latestAddedDate).length;
    render();
  })
  .catch(() => {
    document.querySelector("#last-updated").textContent = "数据读取失败，请通过本地服务器打开网站";
  });

document.querySelectorAll(".filter").forEach(button => button.addEventListener("click", () => {
  if (button.dataset.filter) {
    button.closest(".filters").querySelector(".active").classList.remove("active");
    button.classList.add("active");
    state.filter = button.dataset.filter;
  } else if (button.dataset.relevance) {
    button.closest(".filters").querySelector(".active").classList.remove("active");
    button.classList.add("active");
    state.relevance = button.dataset.relevance;
  } else if (button.dataset.dateRange) {
    button.closest(".filters").querySelector(".active").classList.remove("active");
    button.classList.add("active");
    state.dateRange = button.dataset.dateRange;
    state.dateFrom = "";
    state.dateTo = "";
    document.querySelector("#date-from").value = "";
    document.querySelector("#date-to").value = "";
  }
  render();
}));

["date-from", "date-to"].forEach(id => document.querySelector(`#${id}`).addEventListener("change", event => {
  state[id === "date-from" ? "dateFrom" : "dateTo"] = event.target.value;
  state.dateRange = "custom";
  document.querySelector(".date-filters .active")?.classList.remove("active");
  render();
}));
