/* -*- coding: utf-8 -*- */
/**
 * @file    controls.js
 * @brief   控制栏模块
 * @details 实现底部控制栏的交互逻辑，包括：
 *          - 语音朗读按钮（TTS）
 *          - 自动漫游按钮（AutoWalk）
 *          - 军队选择器
 *          - 留言板
 *          - 底图切换
 * @author  长征文化数字地图项目组
 * @date    2026-07-15
 */

/** @type {string|null} 当前激活的控制模式 */
let activeControl = null;

/** @type {Object|null} 自动漫游状态 */
let autowalkState = {
    active:     false,
    army:       1,
    segmentIdx: 0,
    segments:   [],
    timer:      null,
    marker:     null,
};

/** @type {boolean} 留言板是否打开 */
let messageBoardOpen = false;

/**
 * @function initControls
 * @brief 初始化控制栏事件绑定
 */
function initControls() {
    // 语音朗读按钮
    document.getElementById("btn-tts")?.addEventListener("click", () => {
        if (activeControl === "tts") {
            stopSpeech();
            setActiveControl(null);
        } else {
            if (!window.currentNodeData) {
                alert("请先点击选择一个节点");
                return;
            }
            setActiveControl("tts");
            readCurrentStep();
        }
    });

    // 自动漫游按钮
    document.getElementById("btn-autowalk")?.addEventListener("click", () => {
        if (autowalkState.active) {
            stopAutowalk();
        } else {
            startAutowalk();
        }
    });

    // 军队选择按钮
    document.getElementById("btn-army")?.addEventListener("click", () => {
        toggleArmySelector();
    });

    // 留言板按钮
    document.getElementById("btn-message")?.addEventListener("click", () => {
        toggleMessageBoard();
    });

    // 底图切换按钮
    document.getElementById("btn-basemap")?.addEventListener("click", () => {
        toggleBasemap();
    });

    // 节点面板的上一步/下一步按钮
    document.getElementById("btn-prev-step")?.addEventListener("click", () => {
        prevStep();
    });
    document.getElementById("btn-next-step")?.addEventListener("click", () => {
        nextStep();
    });

    // 节点面板关闭按钮
    document.getElementById("btn-close-panel")?.addEventListener("click", () => {
        closeNodePanel();
    });

    // 节点面板朗读按钮
    document.getElementById("btn-read")?.addEventListener("click", () => {
        readCurrentStep();
    });

    // 节点面板星火投稿按钮
    document.getElementById("btn-spark")?.addEventListener("click", () => {
        openSparkForm();
    });

    console.log("[Controls] 控制栏初始化完成");
}

/**
 * @function setActiveControl
 * @brief 设置当前激活的控制模式（高亮按钮）
 * @param {string|null} ctrl 控制名称
 */
function setActiveControl(ctrl) {
    activeControl = ctrl;

    // 更新按钮高亮状态
    document.querySelectorAll(".ctrl-btn").forEach(btn => {
        btn.classList.remove("active");
    });

    if (ctrl === "tts") {
        document.getElementById("btn-tts")?.classList.add("active");
    } else if (ctrl === "autowalk") {
        document.getElementById("btn-autowalk")?.classList.add("active");
    } else if (ctrl === "message") {
        document.getElementById("btn-message")?.classList.add("active");
    }
}

// ============================================================================
// 自动漫游
// ============================================================================

/**
 * @function startAutowalk
 * @brief 启动自动漫游（图标沿路线移动）
 * @async
 */
async function startAutowalk() {
    const army = autowalkState.army || 1;

    // 获取漫游路径
    let pathData;
    try {
        const resp = await fetch(`/api/v1/routes/autowalk?army=${army}&speed_kmh=30`);
        const json = await resp.json();
        if (json.code !== 0 || !json.data) {
            console.error("[Autowalk] 获取路径失败:", json);
            return;
        }
        pathData = json.data;
    } catch (err) {
        console.error("[Autowalk] 网络错误:", err);
        return;
    }

    if (!pathData.segments || pathData.segments.length === 0) {
        alert("该军队暂无路线数据");
        return;
    }

    autowalkState = {
        active:     true,
        army:       army,
        segmentIdx: 0,
        segments:   pathData.segments,
        totalKm:    pathData.total_km,
        timer:      null,
        marker:     null,
    };

    setActiveControl("autowalk");
    showAutowalkStatus(pathData);

    // 创建移动图标
    const firstSeg = pathData.segments[0];
    autowalkState.marker = L.marker([firstSeg.lat, firstSeg.lng], {
        icon: L.divIcon({
            html: `<div style="
                width:20px;height:20px;
                background:#c0392b;border:2px solid white;
                border-radius:50%;
                box-shadow:0 0 8px rgba(192,57,43,0.8);
            "></div>`,
            className: "",
            iconSize: [20, 20],
            iconAnchor: [10, 10],
        }),
    }).addTo(map.instance);

    // 每 2 秒移动到下一个点
    moveToNextSegment();
    console.log(`[Autowalk] 启动，军队=${army}，共${pathData.segments.length}段`);
}

/**
 * @function moveToNextSegment
 * @brief 移动到下一个路线点
 */
function moveToNextSegment() {
    const state = autowalkState;
    if (!state.active || !state.segments.length) return;

    const idx = state.segmentIdx;
    const segs = state.segments;

    if (idx >= segs.length) {
        // 到达终点
        stopAutowalk();
        return;
    }

    const seg = segs[idx];

    // 移动标记
    if (state.marker) {
        state.marker.setLatLng([seg.lat, seg.lng]);
    }

    // 更新进度条
    updateAutowalkProgress(idx + 1, segs.length, seg.title);

    // 如果有节点数据，显示对应面板
    if (seg.node_id) {
        fetch(`/api/v1/nodes/${seg.node_id}`)
            .then(r => r.json())
            .then(json => {
                if (json.data) showNodePanel(json.data);
            });
    }

    // 飞行到当前位置
    map.instance.panTo([seg.lat, seg.lng], { animate: true });

    // 2.5 秒后移动到下一个点（模拟30km/h）
    const delayMs = 2500;
    state.timer = setTimeout(() => {
        state.segmentIdx++;
        moveToNextSegment();
    }, delayMs);
}

/**
 * @function stopAutowalk
 * @brief 停止自动漫游
 */
function stopAutowalk() {
    if (autowalkState.marker) {
        map.instance.removeLayer(autowalkState.marker);
        autowalkState.marker = null;
    }
    if (autowalkState.timer) {
        clearTimeout(autowalkState.timer);
        autowalkState.timer = null;
    }
    autowalkState.active = false;
    setActiveControl(null);
    hideAutowalkStatus();
    console.log("[Autowalk] 已停止");
}

/**
 * @function showAutowalkStatus
 * @brief 显示自动漫游状态栏
 * @param {Object} pathData 路径数据
 */
function showAutowalkStatus(pathData) {
    const el = document.getElementById("autowalk-status");
    if (!el) return;
    el.querySelector(".army-name").textContent = pathData.name || "长征路线";
    el.querySelector(".progress-bar").style.width = "0%";
    el.querySelector(".segment-info").textContent = `0 / ${pathData.segments.length}`;
    el.classList.add("visible");
}

/**
 * @function updateAutowalkProgress
 * @brief 更新自动漫游进度
 * @param {number} current 当前段索引
 * @param {number} total   总段数
 * @param {string} title   当前节点名称
 */
function updateAutowalkProgress(current, total, title) {
    const el = document.getElementById("autowalk-status");
    if (!el) return;
    const pct = (current / total) * 100;
    el.querySelector(".progress-bar").style.width = `${pct}%`;
    el.querySelector(".segment-info").textContent = `${current} / ${total}`;
    el.querySelector(".current-title").textContent = title || "";
}

/**
 * @function hideAutowalkStatus
 * @brief 隐藏自动漫游状态栏
 */
function hideAutowalkStatus() {
    document.getElementById("autowalk-status")?.classList.remove("visible");
}

// ============================================================================
// 军队选择器
// ============================================================================

/**
 * @function toggleArmySelector
 * @brief 显示/隐藏军队选择器
 */
function toggleArmySelector() {
    const el = document.getElementById("army-selector");
    if (!el) return;

    if (el.classList.contains("visible")) {
        el.classList.remove("visible");
    } else {
        el.classList.add("visible");
    }
}

/**
 * @function selectArmy
 * @brief 选择军队并更新路线显示
 * @param {number} army 军队编号
 */
function selectArmy(army) {
    autowalkState.army = army;

    // 更新 UI 选中状态
    document.querySelectorAll(".army-item").forEach(item => {
        item.classList.toggle("active", parseInt(item.dataset.army) === army);
    });

    // 切换地图路线
    toggleArmy(army);

    // 关闭选择器
    document.getElementById("army-selector")?.classList.remove("visible");

    console.log(`[Army] 已选择军队: ${army}`);
}

// ============================================================================
// 留言板
// ============================================================================

/**
 * @function toggleMessageBoard
 * @brief 显示/隐藏留言板
 */
function toggleMessageBoard() {
    const el = document.getElementById("message-board");
    if (!el) return;

    messageBoardOpen = !messageBoardOpen;
    el.classList.toggle("visible", messageBoardOpen);
    setActiveControl(messageBoardOpen ? "message" : null);

    if (messageBoardOpen) {
        loadMessages();
    }
}

/**
 * @function loadMessages
 * @brief 加载留言数据（模拟）
 */
function loadMessages() {
    const list = document.querySelector(".message-list");
    if (!list) return;

    // 模拟数据
    list.innerHTML = `
        <div class="message-item">
            <span class="msg-user">游客张三</span>
            <span class="msg-time">2026-07-15</span>
            <div style="margin-top:4px">这里是长征的出发地，瑞金！</div>
        </div>
        <div class="message-item">
            <span class="msg-user">历史爱好者</span>
            <span class="msg-time">2026-07-14</span>
            <div style="margin-top:4px">湘江战役是长征途中最惨烈的战役之一</div>
        </div>
    `;
}

/**
 * @function sendMessage
 * @brief 发送留言
 */
function sendMessage() {
    const input = document.querySelector(".message-input-row input");
    const text  = input?.value.trim();
    if (!text) return;

    // TODO: 调用后端 API 提交留言
    console.log("[Message] 发送:", text);
    input.value = "";

    // 乐观更新 UI
    const list = document.querySelector(".message-list");
    if (list) {
        const now = new Date().toLocaleDateString("zh-CN");
        list.innerHTML = `
            <div class="message-item">
                <span class="msg-user">我</span>
                <span class="msg-time">${now}</span>
                <div style="margin-top:4px">${escapeHtml(text)}</div>
            </div>
        ` + list.innerHTML;
    }
}

// ============================================================================
// 底图切换
// ============================================================================

/**
 * @function toggleBasemap
 * @brief 循环切换底图类型: 卫星 → OSM → 暗色
 */
function toggleBasemap() {
    const btn = document.getElementById("btn-basemap");
    const label = btn?.querySelector(".label");
    var types = ["satellite", "osm", "dark"];
    var names = ["标准", "卫星", "暗色"];
    if (!window._baseLayerType) window._baseLayerType = 0;
    window._baseLayerType = (window._baseLayerType + 1) % types.length;
    if (label) label.textContent = names[window._baseLayerType];
    switchBaseLayer(types[window._baseLayerType]);
}

// 初始化
window.initControls   = initControls;
window.startAutowalk  = startAutowalk;
window.stopAutowalk   = stopAutowalk;
window.selectArmy     = selectArmy;
window.toggleMessageBoard = toggleMessageBoard;
window.sendMessage    = sendMessage;
