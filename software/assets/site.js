(() => {
  "use strict";

  const normalize = (value) => String(value || "").toLocaleLowerCase();

  async function loadJson(url) {
    const response = await fetch(url, { credentials: "same-origin" });
    if (!response.ok) throw new Error(`Unable to load ${url}: ${response.status}`);
    return response.json();
  }

  function setupSearch() {
    const indexUrl = document.body.dataset.searchIndex;
    const input = document.querySelector("#search-input");
    const results = document.querySelector("#search-results");
    const summary = document.querySelector("#search-summary");
    if (!indexUrl || !(input instanceof HTMLInputElement) || !results || !summary) return;

    loadJson(indexUrl)
      .then((documents) => {
        const records = documents.map((document) => ({
          ...document,
          haystack: normalize([
            document.title,
            document.slug,
            document.collection,
            document.module_id,
            document.role,
            ...(document.headings || []),
            document.text,
          ].join(" ")),
        }));

        function render() {
          const query = normalize(input.value).trim();
          results.replaceChildren();
          if (!query) {
            summary.textContent = `${records.length} documents indexed.`;
            return;
          }
          const terms = query.split(/\s+/).filter(Boolean);
          const matches = records
            .map((record) => {
              let score = 0;
              const title = normalize(record.title);
              const slug = normalize(record.slug);
              for (const term of terms) {
                if (!record.haystack.includes(term)) return null;
                if (title.includes(term)) score += 8;
                if (slug.includes(term)) score += 5;
                score += Math.min(4, record.haystack.split(term).length - 1);
              }
              return { record, score };
            })
            .filter(Boolean)
            .sort((left, right) => right.score - left.score || left.record.title.localeCompare(right.record.title))
            .slice(0, 50);

          summary.textContent = `${matches.length} result${matches.length === 1 ? "" : "s"}.`;
          for (const match of matches) {
            const item = document.createElement("li");
            const link = document.createElement("a");
            link.href = match.record.url;
            link.textContent = match.record.title;
            const meta = document.createElement("p");
            meta.textContent = [match.record.collection, match.record.module_id, match.record.role]
              .filter(Boolean)
              .join(" · ");
            item.append(link, meta);
            results.append(item);
          }
        }

        input.addEventListener("input", render);
        render();
      })
      .catch((error) => {
        summary.textContent = "Search index could not be loaded.";
        console.error(error);
      });
  }

  function setupGraph() {
    const indexUrl = document.body.dataset.graphIndex;
    const canvas = document.querySelector("#graph-canvas");
    if (!indexUrl || !(canvas instanceof HTMLElement)) return;

    loadJson(indexUrl)
      .then(({ nodes, edges }) => {
        if (!Array.isArray(nodes) || !Array.isArray(edges) || nodes.length === 0) return;
        const width = 1100;
        const height = 620;
        const radius = Math.min(width, height) * 0.38;
        const centerX = width / 2;
        const centerY = height / 2;
        const ns = ["http:", "", "www.w3.org", "2000", "svg"].join("/");
        const svg = document.createElementNS(ns, "svg");
        svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
        svg.setAttribute("aria-hidden", "true");

        const positions = new Map();
        nodes.forEach((node, index) => {
          const angle = -Math.PI / 2 + (index / nodes.length) * Math.PI * 2;
          positions.set(node.id, {
            x: centerX + Math.cos(angle) * radius,
            y: centerY + Math.sin(angle) * radius,
          });
        });

        for (const edge of edges) {
          const source = positions.get(edge.source);
          const target = positions.get(edge.target);
          if (!source || !target) continue;
          const line = document.createElementNS(ns, "line");
          line.setAttribute("x1", source.x);
          line.setAttribute("y1", source.y);
          line.setAttribute("x2", target.x);
          line.setAttribute("y2", target.y);
          line.setAttribute("class", `graph-edge graph-edge-${edge.type}`);
          svg.append(line);
        }

        for (const node of nodes) {
          const position = positions.get(node.id);
          if (!position) continue;
          const link = document.createElementNS(ns, "a");
          link.setAttribute("href", node.url);
          link.setAttribute("class", "graph-node");
          const circle = document.createElementNS(ns, "circle");
          circle.setAttribute("cx", position.x);
          circle.setAttribute("cy", position.y);
          circle.setAttribute("r", "25");
          const label = document.createElementNS(ns, "text");
          label.setAttribute("x", position.x);
          label.setAttribute("y", position.y + 4);
          label.setAttribute("text-anchor", "middle");
          label.textContent = String(node.id).slice(0, 2);
          const title = document.createElementNS(ns, "title");
          title.textContent = `${node.id}: ${node.title}`;
          link.append(circle, label, title);
          svg.append(link);
        }
        canvas.replaceChildren(svg);
      })
      .catch((error) => {
        canvas.textContent = "Graph data could not be loaded. The accessible relationship list remains available below.";
        console.error(error);
      });
  }

  setupSearch();
  setupGraph();
})();
