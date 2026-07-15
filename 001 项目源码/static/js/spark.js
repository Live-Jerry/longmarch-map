/* -*- coding: utf-8 -*- */
/**
 * @file    spark.js
 * @brief   星火拾遗模块 — V1.0.1
 * @details 用户贡献内容对话框：新建节点或补充既有节点。
 *          完整展示节点数据Schema的所有域，提供文件上传入口。
 *          提交后进入待审核，管理员可逐项审核通过或驳回。
 */

// ============================================================================
// 对话框控制
// ============================================================================

/**
 * @function openSparkForm
 * @brief 打开星火拾遗对话框，预填当前选中节点
 */
function openSparkForm() {
    const modal = document.getElementById("spark-modal");
    if (!modal) return;

    modal.style.display = "flex";
    document.body.style.overflow = "hidden";

    // 如果当前有选中节点，预填"补充既有节点"模式
    const activeNode = window.activeNode;
    const select = document.getElementById("spark-node-select");
    if (select) {
        // 填充节点下拉列表
        populateNodeSelect(select, activeNode?.node_id || null);
    }

    // 重置状态提示
    const statusEl = document.getElementById("spark-submit-status");
    if (statusEl) statusEl.textContent = "";
}

/**
 * @function closeSparkForm
 * @brief 关闭星火拾遗对话框
 */
function closeSparkForm() {
    const modal = document.getElementById("spark-modal");
    if (!modal) return;
    modal.style.display = "none";
    document.body.style.overflow = "";
}

/**
 * @function switchSparkTab
 * @brief 切换新建节点 / 补充既有节点 标签页
 * @param {string} tab "new-node" 或 "update-node"
 */
function switchSparkTab(tab) {
    // 切换标签按钮高亮
    document.querySelectorAll(".spark-tab").forEach(function(btn) {
        btn.classList.toggle("active", btn.dataset.tab === tab);
    });

    // 切换字段显示
    document.getElementById("spark-fields-new").style.display =
        tab === "new-node" ? "block" : "none";
    document.getElementById("spark-fields-update").style.display =
        tab === "update-node" ? "block" : "none";

    // 更新隐藏字段
    const hidden = document.querySelector("#spark-form input[name='submission_type']");
    if (hidden) hidden.value = tab;
}

/**
 * @function populateNodeSelect
 * @brief 填充节点下拉选择框
 * @param {HTMLSelectElement} select 选择框元素
 * @param {string|null} activeId 当前激活节点的 node_id
 */
function populateNodeSelect(select, activeId) {
    if (!window.allNodes && window.nodes) {
        window.allNodes = window.nodes;
    }
    const nodes = window.allNodes || [];
    select.innerHTML = '\x3Coption value="">—— 请选择节点 ——\x3C/option>';
    nodes.forEach(function(n) {
        var opt = document.createElement("option");
        opt.value = n.node_id;
        opt.textContent = n.node_id + " " + (n.title || n.location || "");
        if (activeId && n.node_id === activeId) opt.selected = true;
        select.appendChild(opt);
    });
}

// ============================================================================
// 经纬度拾取
// ============================================================================

/**
 * @function showLatLngPicker
 * @brief 在地图上点击选择经纬度（临时启用click监听）
 */
function showLatLngPicker() {
    if (!window.map || !window.map.instance) {
        alert("地图尚未加载完成");
        return;
    }
    alert("请在地图上点击位置来选择经纬度");

    var clickHandler = function(e) {
        var lat = e.latlng.lat.toFixed(6);
        var lng = e.latlng.lng.toFixed(6);
        document.getElementById("spark-lat-input").value = lat;
        document.getElementById("spark-lng-input").value = lng;
        document.getElementById("spark-lat").value = lat;
        document.getElementById("spark-lng").value = lng;
        window.map.instance.off("click", clickHandler);
    };
    window.map.instance.on("click", clickHandler);
}

// ============================================================================
// 表单提交
// ============================================================================

/**
 * @function initSparkForm
 * @brief 初始化星火表单提交
 */
function initSparkForm() {
    var form = document.getElementById("spark-form");
    if (!form) return;
    form.addEventListener("submit", submitSparkForm);
}

/**
 * @function submitSparkForm
 * @brief 提交星火表单
 * @param {Event} e
 */
async function submitSparkForm(e) {
    e.preventDefault();
    var statusEl = document.getElementById("spark-submit-status");
    if (!statusEl) return;

    var form = e.target;
    var formData = new FormData(form);
    var submitBtn = form.querySelector("button[type='submit']");
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "提交中...";
    }

    try {
        var resp = await fetch("/api/v1/sparks/full", {
            method: "POST",
            headers: {
                "Authorization": "Bearer " + (window.authToken || "")
            },
            body: formData
        });
        var json = await resp.json();

        if (json.code === 0) {
            statusEl.className = "form-status success";
            statusEl.textContent = "✅ 提交成功！等待管理员审核。";
            // 3秒后关闭
            setTimeout(closeSparkForm, 3000);
        } else {
            statusEl.className = "form-status error";
            statusEl.textContent = "❌ " + (json.message || "提交失败");
        }
    } catch (err) {
        statusEl.className = "form-status error";
        statusEl.textContent = "❌ 网络错误，请重试";
        console.error("[Spark] 提交失败", err);
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.textContent = "提交审核";
        }
    }
}

// ============================================================================
// 初始化
// ============================================================================

document.addEventListener("DOMContentLoaded", function() {
    initSparkForm();
});
