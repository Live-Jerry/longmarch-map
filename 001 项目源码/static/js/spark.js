/* -*- coding: utf-8 -*- */
/**
 * @file    spark.js
 * @brief   节点编辑器 — 共享弹窗控制器
 * @details 支持四种调用类型：
 *          拾遗、新增、查看、编辑
 *          弹窗本身只负责 UI + 数据收集，返回给调用者处理存储逻辑。
 */

// ============================================================================
// 全局状态
// ============================================================================

/** 当前调用类型：'拾遗' | '新增' | '查看' | '编辑' */
var editorCallType = null;

/** 当前操作的节点ID（编辑/查看时使用） */
var editorNodeId = null;

/** 提交回调：function(formElement, callType, mode, nodeId) */
var editorCallback = null;

/** 当前激活的tab：'view' | 'add' | 'edit' */
var editorActiveTab = 'add';

// ============================================================================
// 节点编辑器 打开/关闭
// ============================================================================

/**
 * 打开节点编辑器弹窗
 * @param {string} callType  调用类型：'拾遗' | '新增' | '查看' | '编辑'
 * @param {string|null} nodeId  节点ID（查看/编辑传入已有ID，新增传模板ID，拾遗传null）
 * @param {function} callback   提交回调 function(formElement, callType, mode, nodeId)
 *                                mode 当前tab：'add' 或 'edit'
 */
function openNodeEditor(callType, nodeId, callback) {
    var modal = document.getElementById("node-editor");
    if (!modal) { console.error("[NodeEditor] 弹窗DOM不存在"); return; }

    var form = document.getElementById("node-form");
    if (!form) { console.error("[NodeEditor] 表单不存在"); return; }

    // 保存全局状态
    editorCallType = callType;
    editorNodeId = nodeId || null;
    editorCallback = callback || null;

    // 重置表单状态
    resetForm();

    // 根据调用类型初始化
    if (callType === '拾遗') {
        initSparkMode();
    } else if (callType === '查看') {
        initViewMode(nodeId);
    } else if (callType === '新增') {
        initAddMode(nodeId);
    } else if (callType === '编辑') {
        initEditMode(nodeId);
    }

    modal.style.display = "flex";
    document.body.style.overflow = "hidden";
}

/**
 * 关闭节点编辑器
 */
function closeNodeEditor() {
    var modal = document.getElementById("node-editor");
    if (!modal) return;
    modal.style.display = "none";
    document.body.style.overflow = "";
    editorCallback = null;
}

// ============================================================================
// 四种调用模式的初始化逻辑
// ============================================================================

/**
 * 拾遗模式：查看节点变灰，新增节点+编辑节点开放
 * 新增节点 → 新建 Spark 提交（包含多媒体等）
 * 编辑节点 → 补充既有 Spark 提交
 */
function initSparkMode() {
    document.getElementById("node-editor-title").textContent = "星火拾遗 — 提交您的长征记忆";

    setTabGray('view');
    setTabActive('add');
    setTabEnabled('edit');

    // 上传字段激活，上传者信息显示
    setupMultimediaMode(false);
    document.getElementById("node-submitter-info").style.display = "block";
    document.getElementById("node-submit-btn").style.display = "";
    document.getElementById("node-submit-btn").textContent = "提交审核";

    // 节点 ID 预填模板数据（有选中节点时才加载）
    if (editorNodeId) {
        loadNodeData(editorNodeId, false);
    }

    switchEditorTab('add');
}

/**
 * 查看模式：查看节点激活，新增+编辑变灰
 */
function initViewMode(nodeId) {
    document.getElementById("node-editor-title").textContent = "查看节点 — " + nodeId;

    setTabActive('view');
    setTabGray('add');
    setTabGray('edit');

    // 上传按钮不激活（disabled），同时显示既有文件
    setupMultimediaMode(true);
    document.getElementById("node-submitter-info").style.display = "none";
    document.getElementById("node-submit-btn").style.display = "none";

    switchEditorTab('view');

    // 加载数据（只读）
    loadNodeData(nodeId, true);
    loadExistingMedia(nodeId);
}

/**
 * 新增模式：新增节点激活，查看+编辑变灰
 */
function initAddMode(nodeId) {
    document.getElementById("node-editor-title").textContent = " 新增节点";

    setTabGray('view');
    setTabActive('add');
    setTabGray('edit');

    // 上传字段激活，隐藏上传者信息
    setupMultimediaMode(false);
    document.getElementById("node-submitter-info").style.display = "none";
    document.getElementById("node-submit-btn").style.display = "";
    document.getElementById("node-submit-btn").textContent = "新增";

    switchEditorTab('add');

    // 模板节点数据预填
    loadNodeData(nodeId, false);
}

/**
 * 编辑模式：编辑节点激活，查看+新增变灰
 */
function initEditMode(nodeId) {
    document.getElementById("node-editor-title").textContent = " 编辑节点 — " + nodeId;

    setTabGray('view');
    setTabGray('add');
    setTabActive('edit');

    // 上传字段激活，隐藏上传者信息
    setupMultimediaMode(false);
    document.getElementById("node-submitter-info").style.display = "none";
    document.getElementById("node-submit-btn").style.display = "";
    document.getElementById("node-submit-btn").textContent = "保存";

    switchEditorTab('edit');

    // 加载数据
    loadNodeData(nodeId, false);
    loadExistingMedia(nodeId);
}

// ============================================================================
// Tab 控制
// ============================================================================

function setTabActive(tab) {
    var btns = document.querySelectorAll(".editor-tab");
    btns.forEach(function(b) {
        b.classList.toggle("active", b.dataset.tab === tab);
    });
}

function setTabGray(tab) {
    var btn = document.querySelector('.editor-tab[data-tab="' + tab + '"]');
    if (btn) {
        btn.classList.remove("active");
        btn.classList.add("grayed");
    }
}

function setTabEnabled(tab) {
    var btn = document.querySelector('.editor-tab[data-tab="' + tab + '"]');
    if (btn) {
        btn.classList.remove("grayed");
        btn.classList.remove("active");
    }
}

/**
 * 切换tab
 * @param {string} tab  'view' | 'add' | 'edit'
 */
function switchEditorTab(tab) {
    var btn = document.querySelector('.editor-tab[data-tab="' + tab + '"]');
    // 如果变灰，不允许点击切换
    if (btn && btn.classList.contains("grayed")) return;

    var form = document.getElementById("node-form");
    if (!form) return;

    // 更新激活tab
    setTabActive(tab);
    editorActiveTab = tab;

    // 更新隐藏字段
    var hidden = form.querySelector("input[name='submission_type']");
    if (hidden) hidden.value = tab;

    // 显示/隐藏正确字段组
    // 基础字段总是显示
    // 编辑模式时，如果是 拾遗 类型才显示节点选择器
    if (tab === 'edit' && editorCallType === '拾遗') {
        // node-fields-existing removed; dropdown now in tab bar
        // 隐藏基础字段（拾遗的编辑用选择器选节点）
        // 填充下拉列表，按当前军队过滤
        
        // 下拉框滚动
        document.getElementById("node-select-existing").style.maxHeight = "300px";
        document.getElementById("node-select-existing").style.overflowY = "auto";
        populateNodeSelect(null);
        document.getElementById("node-select-existing").disabled = false;
    } else {
        document.getElementById("node-fields-base").style.display = "block";
    }

    // required 属性控制
    var reqFields = ["node_id", "title", "location", "time"];
    reqFields.forEach(function(name) {
        var el = form.querySelector("[name='" + name + "']");
        if (el) {
            if (tab === 'edit' && editorCallType === '拾遗') {
                el.removeAttribute("required");
            } else if (tab === 'view') {
                // 查看模式：不需要校验
                el.removeAttribute("required");
            } else {
                el.setAttribute("required", "");
            }
        }
    });

    // 查看模式：禁用所有字段
    var allInputs = form.querySelectorAll("input:not([type='hidden']):not([type='file']), textarea, select");
    var isView = (tab === 'view') || (editorCallType === '查看');
    for (var i = 0; i < allInputs.length; i++) {
        allInputs[i].disabled = isView;
    }
    // 下拉框：只有 拾遗→编辑 才激活，其他全部禁用
    var selectEl = document.getElementById("node-select-existing");
    if (selectEl) {
        if (editorCallType === '\u62fe\u9057' && tab === 'edit') {
            selectEl.disabled = false;
        } else {
            selectEl.disabled = true;
        }
    }

}

// ============================================================================
// 表单重置 / 填充 / 数据加载
// ============================================================================

/**
 * 重置表单到初始状态
 */
function resetForm() {
    var form = document.getElementById("node-form");
    if (!form) return;

    var fields = form.querySelectorAll("input:not([type='hidden']):not([type='file']), textarea, select");
    for (var i = 0; i < fields.length; i++) {
        fields[i].value = "";
        fields[i].disabled = false;
        fields[i].removeAttribute("readonly");
        fields[i].style.background = "";
        fields[i].style.color = "";
    }
    // 恢复 required
    var reqFields = ["node_id", "title", "location", "time"];
    reqFields.forEach(function(name) {
        var el = form.querySelector("[name='" + name + "']");
        if (el) el.setAttribute("required", "");
    });

    document.getElementById("node-submit-status").textContent = "";
    document.getElementById("node-submit-status").className = "form-status";
    document.getElementById("node-submit-btn").disabled = false;
    // removed: node-fields-existing now in tab bar
    document.getElementById("node-fields-base").style.display = "block";
    document.getElementById("node-submit-btn").style.display = "";

    // 重置多媒体区域
    document.getElementById("node-existing-media").style.display = "none";
    document.getElementById("node-existing-media-list").innerHTML = "";
    document.getElementById("node-existing-media").style.background = "";
    document.getElementById("node-existing-media").style.border = "";
    document.getElementById("node-upload-fields").style.display = "block";
    // 重置 file inputs
    var fileInputs = form.querySelectorAll("input[type='file']");
    for (var i = 0; i < fileInputs.length; i++) {
        fileInputs[i].value = "";
        fileInputs[i].disabled = false;
    }

    // 清除 tab gray 状态
    document.querySelectorAll(".editor-tab").forEach(function(b) {
        b.classList.remove("grayed");
    });
}

/**
 * 设置多媒体区域状态
 * @param {boolean} isView  true=查看模式（上传按钮不激活，显示既有文件）
 *                           false=新增/编辑/拾遗模式（上传按钮激活）
 */
function setupMultimediaMode(isView) {
    var uploadDiv = document.getElementById("node-upload-fields");
    var existingDiv = document.getElementById("node-existing-media");

    uploadDiv.style.display = "block";
    existingDiv.style.display = "block";

    // 文件输入始终显示，但查看模式禁用了不让点
    var fileInputs = uploadDiv.querySelectorAll("input[type='file']");
    for (var i = 0; i < fileInputs.length; i++) {
        fileInputs[i].disabled = isView;
    }

    // 查看模式：既有多媒体区突出显示；其他模式：简单展示
    if (isView) {
        existingDiv.style.background = "rgba(255,255,255,0.06)";
        existingDiv.style.border = "1px solid rgba(255,255,255,0.1)";
    } else {
        existingDiv.style.background = "";
        existingDiv.style.border = "";
    }
}

/**
 * 加载节点的已有关联媒体文件
 * @param {string} nodeId
 */
function loadExistingMedia(nodeId) {
    var listEl = document.getElementById("node-existing-media-list");
    var container = document.getElementById("node-existing-media");
    if (!listEl || !container) return;

    container.style.display = "block";
    listEl.innerHTML = "<div style='color:#95a5a6;font-size:12px'>加载中...</div>";

    var token = localStorage.getItem("lm_token");
    fetch("/api/v1/media/node/" + encodeURIComponent(nodeId), {
        headers: { "Authorization": "Bearer " + token }
    })
        .then(function(r) { return r.json(); })
        .then(function(j) {
            if (j.code !== 0 || !j.data || !j.data.items || !j.data.items.length) {
                listEl.innerHTML = "<div style='color:#666;font-size:12px'>暂无关联媒体</div>";
                return;
            }
            var html = "";
            j.data.items.forEach(function(m) {
                var icon = "";
                if (m.type === "image") icon = "";
                else if (m.type === "video") icon = "";
                else if (m.type === "audio") icon = "";
                html += "<div style='padding:4px 0;font-size:12px;color:#ecf0f1'>" +
                    icon + " " + m.title + "</div>";
            });
            listEl.innerHTML = html;
        })
        .catch(function() {
            listEl.innerHTML = "<div style='color:#666;font-size:12px'>加载失败</div>";
        });
}

/**
 * 从 API 加载节点数据并填充到表单
 * @param {string} nodeId
 * @param {boolean} readOnly  是否只读模式
 */
function loadNodeData(nodeId, readOnly) {
    var form = document.getElementById("node-form");
    if (!form) return;

    var token = localStorage.getItem("lm_token");

    fetch("/api/v1/nodes/" + nodeId, { headers: { "Authorization": "Bearer " + token } })
        .then(function(r) { return r.json(); })
        .then(function(j) {
            if (j.code !== 0 || !j.data) {
                alert("获取节点失败：" + (j.message || "未知错误"));
                return;
            }
            fillForm(j.data, readOnly);
        })
        .catch(function() {
            alert("网络错误，获取节点失败");
        });
}

/**
 * 填充表单字段
 * @param {object} data  节点数据对象
 * @param {boolean} readOnly  是否只读（禁用+只读样式）
 */
function fillForm(data, readOnly) {
    var form = document.getElementById("node-form");
    if (!form) return;

    var fieldMap = [
        "node_id", "title", "location", "time",
        "core_numbers", "famous_battle", "important_meeting",
        "history_event", "core_site", "poem_article",
        "typical_story", "typical_people", "historical_significance"
    ];

    fieldMap.forEach(function(name) {
        var el = form.querySelector("[name='" + name + "']");
        if (el) {
            var v = data[name];
            el.value = v !== undefined && v !== null ? String(v) : "";
        }
    });

    // 经纬度
    var latEl = form.querySelector("[name='lat_input']");
    var lngEl = form.querySelector("[name='lng_input']");
    if (latEl) latEl.value = data.lat !== undefined ? String(data.lat) : "";
    if (lngEl) lngEl.value = data.lng !== undefined ? String(data.lng) : "";
    // 隐藏经纬度也同步
    var latHide = document.getElementById("node-lat");
    var lngHide = document.getElementById("node-lng");
    if (latHide) latHide.value = data.lat || "";
    if (lngHide) lngHide.value = data.lng || "";

    // 只读模式：禁用所有输入
    if (readOnly) {
        var allEls = form.querySelectorAll("input:not([type='hidden']):not([type='file']), textarea, select");
        for (var i = 0; i < allEls.length; i++) {
            allEls[i].disabled = true;
        }
    }

    // 编辑模式：node_id 只读
    if (editorCallType === '编辑') {
        var nodeIdEl = form.querySelector("[name='node_id']");
        if (nodeIdEl) {
            nodeIdEl.setAttribute("readonly", "readonly");
            nodeIdEl.style.background = "rgba(255,255,255,0.03)";
            nodeIdEl.style.color = "#95a5a6";
        }
    }
}

// ============================================================================
// 经纬度拾取（从地图点击）
// ============================================================================

function showLatLngPicker() {
    if (!window.map || !window.map.instance) {
        alert("地图尚未加载完成");
        return;
    }
    // 如果不在首页（无地图），提示
    if (editorCallType !== '拾遗') {
        // 管理后台无地图，允许手动输入
        return;
    }
    alert("请在地图上点击位置来选择经纬度");

    var clickHandler = function(e) {
        var lat = e.latlng.lat.toFixed(6);
        var lng = e.latlng.lng.toFixed(6);
        document.getElementById("node-lat-input").value = lat;
        document.getElementById("node-lng-input").value = lng;
        document.getElementById("node-lat").value = lat;
        document.getElementById("node-lng").value = lng;
        window.map.instance.off("click", clickHandler);
    };
    window.map.instance.on("click", clickHandler);
}

// ============================================================================
// 表单提交
// ============================================================================

function initNodeForm() {
    var form = document.getElementById("node-form");
    if (!form) return;
    form.addEventListener("submit", handleNodeFormSubmit);
}

function handleNodeFormSubmit(e) {
    e.preventDefault();

    // 查看模式不能提交
    if (editorCallType === '查看') return;
    if (editorActiveTab === 'view') return;

    var statusEl = document.getElementById("node-submit-status");
    if (!statusEl) return;

    var form = e.target;
    var submitBtn = document.getElementById("node-submit-btn");

    // 同步经纬度
    var latInput = form.querySelector("[name='lat_input']");
    var lngInput = form.querySelector("[name='lng_input']");
    var latHide = document.getElementById("node-lat");
    var lngHide = document.getElementById("node-lng");
    if (latHide && latInput) latHide.value = latInput.value;
    if (lngHide && lngInput) lngHide.value = lngInput.value;

    // 如果有回调，把控制权交给调用者
    if (typeof editorCallback === 'function') {
        try {
            var mode = editorActiveTab;
            // 拾遗+编辑模式传 target_node_id
            var actualNodeId = editorNodeId;
            if (editorCallType === '拾遗' && mode === 'edit') {
                var existing = document.getElementById("node-select-existing");
                if (existing) actualNodeId = existing.value;
            }
            editorCallback(form, editorCallType, mode, actualNodeId);
        } catch (err) {
            statusEl.className = "form-status error";
            statusEl.textContent = " " + (err.message || "提交失败");
            console.error("[NodeEditor] 提交错误", err);
        }
    } else {
        statusEl.className = "form-status error";
        statusEl.textContent = "未设置提交回调，无法处理数据";
    }
}

// ============================================================================
// 节点下拉列表填充
// ============================================================================

function populateNodeSelect(activeId) {
    var select = document.getElementById("node-select-existing");
    if (!select) return;

    var nodes = window.allNodes || window.nodes || [];
    // 获取当前选中军队
    var currentArmy = 0;
    if (typeof autowalkState !== 'undefined' && autowalkState) {
        currentArmy = autowalkState.army || 0;
    }

    // army name -> number 映射（与 map.js 保持一致）
    var armyMap = {"\u4e2d\u592e\u7ea2\u519b\uff08\u7ea2\u4e00\u65b9\u9762\u519b\uff09":1,"\u4e2d\u592e\u7ea2\u519b":1,"\u7ea2\u4e8c\u65b9\u9762\u519b":2,"\u7ea2\u56db\u65b9\u9762\u519b":4,"\u7ea225\u519b":25};

    select.innerHTML = '<option value="">—— 请选择节点 ——</option>';
    nodes.forEach(function(n) {
        // 按军队过滤
        var nArmyNum = armyMap[n.army] || 0;
        if (currentArmy !== 0 && nArmyNum !== currentArmy) return;

        var opt = document.createElement("option");
        opt.value = n.node_id;
        opt.textContent = n.node_id + " " + (n.title || n.location || "");
        if (activeId && n.node_id === activeId) opt.selected = true;
        select.appendChild(opt);
    });

    // 选中节点后自动加载数据
    select.onchange = function() {
        var val = this.value;
        if (val) {
            loadNodeData(val, false);
        }
    };
}

// ============================================================================
// 初始化
// ============================================================================

document.addEventListener("DOMContentLoaded", function() {
    initNodeForm();
});

// ============================================================================
// 向后兼容别名（旧版本代码调用 openSparkForm / closeSparkForm）
// ============================================================================

function openSparkForm() {
    openNodeEditor('拾遗', null, typeof sparkSubmitCallback !== 'undefined' ? sparkSubmitCallback : null);
}

function closeSparkForm() {
    closeNodeEditor();
}

function switchSparkTab(tab) {
    var t = tab === 'new-node' ? 'add' : 'edit';
    switchEditorTab(t);
}
