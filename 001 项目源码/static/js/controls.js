/* -*- coding: utf-8 -*- */
/**
 * @file    controls.js
 * @brief   控制栏模块 — V1.1.0
 * @details 右侧控制栏交互逻辑。
 *          自动漫游：按节点间时间（3s/2s/1s）匀速移动，语音关时停留8s，
 *          语音开时朗读全部内容后继续。
 */

/** @type {string|null} 当前激活的控制模式 */
let activeControl = null;

/** @type {boolean} 留言板是否打开 */
let messageBoardOpen = false;

/** @type {number} 当前选中速度（秒/节点对） */
let autowalkSpeed = 3;

/**
 * @struct AutowalkState
 * @brief  自动漫游状态
 */
let autowalkState = {
    active:     false,     // 漫游是否激活
    paused:     false,     // 是否暂停
    speed:      3,         // 秒/节点对
    army:       1,         // 军队编号
    nodes:      [],        // [{node_id, title, lat, lng}, ...] 有序节点列表
    routePts:   [],        // [{lat, lng}, ...] 全部路线点
    nodeIdx:    0,         // 当前目标节点索引（即将到达的节点）
    segStart:   null,      // {lat, lng} 当前段起点
    segEnd:     null,      // {lat, lng} 当前段终点（下一节点位置）
    segDuration: 3000,     // 当前段时长 ms
    animFrame:  null,      // requestAnimationFrame id
    animStart:  null,      // 当前段开始时间
    marker:     null,      // Leaflet 移动标记
    waiting:    false,     // 是否在节点停留等待
    waitTimer:  null,      // 停留定时器
};

// ============================================================================
// 初始化
// ============================================================================

/**
 * @function initControls
 * @brief 初始化控制栏事件绑定
 */
function initControls() {
    // 全局语音开关：打开/关闭自动朗读（漫游或手动激活节点时）
    document.getElementById("btn-tts")?.addEventListener("click", () => {
        const ttsBtn = document.getElementById("btn-tts");
        const isOn = ttsBtn?.classList.contains("active");
        
        if (isOn) {
            // 关闭语音
            ttsBtn.classList.remove("active");
            stopSpeech();
            if (typeof window.voiceEnabled !== "undefined") {
                window.voiceEnabled = false;
            }
        } else {
            // 打开语音
            ttsBtn.classList.add("active");
            if (typeof window.voiceEnabled !== "undefined") {
                window.voiceEnabled = true;
            }
            // 如果有已激活的节点，立即朗读
            if (window.currentNodeData && typeof readCurrentContent === "function") {
                readCurrentContent();
            }
        }
    });

    document.getElementById("btn-autowalk")?.addEventListener("click", () => {
        if (!autowalkState.active) {
            // 首次点击：显示速度选择
            showSpeedSelector();
        } else {
            // 已激活：暂停/继续
            togglePause();
        }
    });

    // 播放控制：暂停
    document.getElementById("btn-play-pause")?.addEventListener("click", togglePause);
    // 播放控制：跳过
    document.getElementById("btn-skip")?.addEventListener("click", skipToNext);
    // 播放控制：重头
    document.getElementById("btn-restart")?.addEventListener("click", restartAutowalk);
    // 军队选择
    document.getElementById("btn-army")?.addEventListener("click", toggleArmySelector);
    // 星火拾遗
    document.getElementById("btn-spark-main")?.addEventListener("click", () => {
        if (typeof openSparkForm === "function") {
            openSparkForm();
        } else {
            alert("请先点击选择一个节点");
        }
    });
    // 退出自动漫游
    document.getElementById("btn-exit-autowalk")?.addEventListener("click", stopAutowalk);
    // 留言板
    document.getElementById("btn-message")?.addEventListener("click", toggleMessageBoard);
    // 底图切换
    document.getElementById("btn-basemap")?.addEventListener("click", toggleBasemap);
    // 面板关闭
    document.getElementById("btn-close-panel")?.addEventListener("click", closeNodePanel);
    // 面板朗读
    document.getElementById("btn-read")?.addEventListener("click", () => {
        if (typeof readCurrentContent === "function") readCurrentContent();
    });
    // 星火投稿
    document.getElementById("btn-spark")?.addEventListener("click", () => {
        if (typeof openSparkForm === "function") openSparkForm();
    });

    // 初始化全局语音状态
    window.voiceEnabled = false;

    console.log("[Controls] 控制栏初始化完成");
}

/**
 * @function setActiveControl
 * @brief 设置当前激活的控制模式（高亮按钮）
 * @param {string|null} ctrl 控制名称
 */
function setActiveControl(ctrl) {
    activeControl = ctrl;
    document.querySelectorAll(".ctrl-btn").forEach(btn => btn.classList.remove("active"));
    if (ctrl === "tts") {
        document.getElementById("btn-tts")?.classList.add("active");
    } else if (ctrl === "message") {
        document.getElementById("btn-message")?.classList.add("active");
    }
}

// ============================================================================
// 速度选择
// ============================================================================

/**
 * @function showSpeedSelector
 * @brief 显示速度选择器（向左弹出），用户选择后开始漫游
 */
function showSpeedSelector() {
    const ss = document.getElementById("speed-selector");
    if (!ss) return;

    // 定位到漫游按钮左侧
    const btn = document.getElementById("btn-autowalk");
    if (btn) {
        const rect = btn.getBoundingClientRect();
        ss.style.top = rect.top + "px";
        ss.style.right = (window.innerWidth - rect.left + 8) + "px";
        ss.style.left = "auto";
        ss.style.bottom = "auto";
    }

    ss.classList.add("visible");

    // 高亮当前速度
    document.querySelectorAll(".speed-btn").forEach(btn => {
        btn.classList.toggle("active", parseInt(btn.dataset.speed) === autowalkSpeed);
    });
}

/**
 * @function setAutowalkSpeed
 * @brief 选择漫游速度并开始
 * @param {number} seconds 每节点对移动时间
 */
function selectAutowalkSpeed(seconds) {
    autowalkSpeed = seconds;
    document.querySelectorAll(".speed-btn").forEach(btn => {
        btn.classList.toggle("active", parseInt(btn.dataset.speed) === seconds);
    });
    // 启用"开始"按钮
    var startBtn = document.getElementById("btn-autowalk-start");
    if (startBtn) startBtn.disabled = false;
}

// ============================================================================
// 自动漫游核心逻辑
// ============================================================================

/**
 * @function startAutowalk
 * @brief 启动自动漫游
 * @async
 */
async function startAutowalk() {
    const army = autowalkState.army || 1;

    // 获取路径数据
    let pathData;
    try {
        const resp = await fetch(`/api/v1/routes/autowalk?army=${army}&speed_kmh=30`);
        const json = await resp.json();
        if (json.code !== 0 || !json.data) {
            console.error("[Autowalk] 获取路径失败");
            return;
        }
        pathData = json.data;
    } catch (err) {
        console.error("[Autowalk] 网络错误:", err);
        return;
    }

    if (!pathData.segments || pathData.segments.length < 2) {
        alert("该军队暂无路线数据");
        return;
    }

    // 提取有序节点列表
    const nodes = [];
    pathData.segments.forEach(seg => {
        if (seg.node_id) {
            nodes.push({
                node_id: seg.node_id,
                title: seg.title || seg.node_id,
                lat: seg.lat,
                lng: seg.lng,
            });
        }
    });

    if (nodes.length < 2) {
        alert("路线节点不足");
        return;
    }

    // 提取全部路线点（用于平滑移动）
    const routePts = pathData.segments.map(s => ({ lat: s.lat, lng: s.lng }));

    // 初始化状态
    autowalkState = {
        active:     true,
        paused:     false,
        speed:      autowalkSpeed,
        army:       army,
        nodes:      nodes,
        routePts:   routePts,
        nodeIdx:    0,      // 从第一个节点出发
        segStart:   { lat: nodes[0].lat, lng: nodes[0].lng },
        segEnd:     { lat: nodes[1].lat, lng: nodes[1].lng },
        segDuration: autowalkSpeed * 1000,
        animFrame:  null,
        animStart:  null,
        marker:     null,
        waiting:    false,
        waitTimer:  null,
    };

    // 显示播放控制按钮（向左弹出）
    document.getElementById("autowalk-label").textContent = "漫游中";
    showPlayControls();

    // 创建移动图标
    const start = nodes[0];
    autowalkState.marker = L.marker([start.lat, start.lng], {
        icon: L.divIcon({
            html: `<div class="autowalk-marker"><div class="autowalk-dot"></div></div>`,
            className: "",
            iconSize: [24, 24],
            iconAnchor: [12, 12],
        }),
    }).addTo(map.instance);

    // 飞到起点
    map.instance.flyTo([start.lat, start.lng], 7, { duration: 1 });

    // 显示状态
    showAutowalkStatus(nodes.length);

    // 先激活第一个节点（让用户看到并等停留结束后再移动）
    setTimeout(() => {
        arriveAtNode(0);
    }, 500);

    console.log(`[Autowalk] 启动，军队=${army}，${nodes.length}个节点，速度=${autowalkSpeed}s/段`);
}

/**
 * @function animateMovement
 * @brief 使用 requestAnimationFrame 沿路径点匀速移动
 * @param {Array} segPts  [{lat, lng}, ...] 当前段路径点
 * @param {number} ptIdx  当前路径点索引
 */
function animateMovement(segPts, ptIdx) {
    if (!autowalkState.active || autowalkState.paused) return;

    const state = autowalkState;

    // 到达终点
    if (ptIdx >= segPts.length) {
        // 到达目标节点
        arriveAtNode(state.nodeIdx + 1);
        return;
    }

    const target = segPts[ptIdx];

    // 移动标记
    if (state.marker) {
        state.marker.setLatLng([target.lat, target.lng]);
    }

    // 更新进度
    const totalPts = segPts.length;
    const progress = ((ptIdx + 1) / totalPts);
    updateAutowalkProgress(state.nodeIdx, state.nodes.length, progress);

    // 跟随地图
    map.instance.panTo([target.lat, target.lng], { animate: false });

    // 计算下一帧延迟（50fps，均匀分配）
    const delay = state.segDuration / totalPts;

    state.animFrame = setTimeout(() => {
        animateMovement(segPts, ptIdx + 1);
    }, delay);
}

/**
 * @function getSegmentRoutePoints
 * @brief 获取两个节点之间的路线点（包含起点，不包含终点）
 * @param {Array} routePts  全部路线点
 * @param {number} fromNodeIdx  起始节点在 nodes[] 中的索引
 * @param {number} toNodeIdx    目标节点在 nodes[] 中的索引
 * @returns {Array} [{lat, lng}, ...]
 */
function getSegmentRoutePoints(routePts, fromNodeIdx, toNodeIdx) {
    const state = autowalkState;
    const fromNode = state.nodes[fromNodeIdx];
    const toNode = state.nodes[toNodeIdx];
    if (!fromNode || !toNode) return [];

    // 在 routePts 中找到两个节点对应的索引
    const eps = 0.001; // 0.001度约 100m 容差
    let fromIdx = -1, toIdx = -1;
    for (let i = 0; i < routePts.length; i++) {
        const p = routePts[i];
        const d1 = Math.abs(p.lat - fromNode.lat) + Math.abs(p.lng - fromNode.lng);
        const d2 = Math.abs(p.lat - toNode.lat) + Math.abs(p.lng - toNode.lng);
        if (d1 < eps && fromIdx === -1) fromIdx = i;
        if (d2 < eps) toIdx = i;
    }

    if (fromIdx === -1 || toIdx === -1 || toIdx <= fromIdx) {
        // 保底：返回两点间的直线插值
        const pts = [];
        const steps = 30;
        for (let i = 0; i < steps; i++) {
            const t = i / steps;
            pts.push({
                lat: fromNode.lat + (toNode.lat - fromNode.lat) * t,
                lng: fromNode.lng + (toNode.lng - fromNode.lng) * t,
            });
        }
        return pts;
    }

    // 返回 fromIdx+1 到 toIdx（不包含起点，包含终点）
    const result = [];
    for (let i = fromIdx + 1; i <= toIdx; i++) {
        result.push({ lat: routePts[i].lat, lng: routePts[i].lng });
    }
    return result;
}

/**
 * @function arriveAtNode
 * @brief 到达节点时的处理
 * @param {number} nodeIdx  节点在 nodes[] 中的索引
 */
function arriveAtNode(nodeIdx) {
    const state = autowalkState;
    if (!state.active) return;

    state.nodeIdx = nodeIdx;

    // 更新进度条
    updateAutowalkProgress(nodeIdx, state.nodes.length, 1);

    // 获取节点数据并显示面板
    const node = state.nodes[nodeIdx];
    if (node && node.node_id) {
        fetch(`/api/v1/nodes/${node.node_id}`)
            .then(r => r.json())
            .then(json => {
                if (json.data && typeof showNodePanel === "function") {
                    showNodePanel(json.data);
                }
            });
    }

    // 判断是否到达最后一个节点
    if (nodeIdx >= state.nodes.length - 1) {
        // 到达终点
        setTimeout(() => {
            alert("已到达终点！");
            stopAutowalk();
        }, 1000);
        return;
    }

    // 准备下一段
    state.segStart = { lat: node.lat, lng: node.lng };
    const nextNode = state.nodes[nodeIdx + 1];
    state.segEnd = { lat: nextNode.lat, lng: nextNode.lng };
    state.segDuration = state.speed * 1000;

    // 等待：语音开则朗读全部内容，否则 8 秒
    state.waiting = true;

    // 判断语音是否开启（TTS 按钮高亮状态）
    const voiceOn = document.getElementById("btn-tts")?.classList.contains("active");

    if (voiceOn) {
        // 语音开启：朗读全部节点内容
        // 收集所有内容文本
        if (node && typeof fetchContentForTTS === "function") {
            fetchContentForTTS(node.node_id, () => {
                // 轮询检查语音是否结束
                checkSpeechDone();
            });
        } else {
            // 朗读面板可见内容
            if (typeof readCurrentContent === "function") {
                readCurrentContent();
            }
            // 每0.5秒检查语音是否结束
            checkSpeechDone(500);
        }
    } else {
        // 语音关闭：停留 8 秒
        state.waitTimer = setTimeout(() => {
            state.waiting = false;
            moveToNextSegment();
        }, 8000);
    }
}

/**
 * @function checkSpeechDone
 * @brief 轮询检查语音是否朗读完毕
 */
function checkSpeechDone() {
    if (!autowalkState.active || !autowalkState.waiting) return;

    if (!window.speechSynthesis || !window.speechSynthesis.speaking) {
        // 语音结束
        autowalkState.waiting = false;
        moveToNextSegment();
        return;
    }

    // 每秒检查一次
    setTimeout(checkSpeechDone, 1000);
}

/**
 * @function moveToNextSegment
 * @brief 移动到下一段
 */
function moveToNextSegment() {
    const state = autowalkState;
    if (!state.active) return;

    const nodeIdx = state.nodeIdx;
    const nextIdx = nodeIdx + 1;

    if (nextIdx >= state.nodes.length) {
        stopAutowalk();
        return;
    }

    state.segStart = { lat: state.nodes[nodeIdx].lat, lng: state.nodes[nodeIdx].lng };
    state.segEnd = { lat: state.nodes[nextIdx].lat, lng: state.nodes[nextIdx].lng };
    state.segDuration = state.speed * 1000;

    // 获取路径点
    const segPts = getSegmentRoutePoints(state.routePts, nodeIdx, nextIdx);

    animateMovement(segPts, 0);
}

/**
 * @function showPlayControls
 * @brief 显示播放控制弹出面板（定位到漫游按钮左侧）
 */
function showPlayControls() {
    const pc = document.getElementById("play-controls");
    if (!pc) return;

    const btn = document.getElementById("btn-autowalk");
    if (btn) {
        const rect = btn.getBoundingClientRect();
        pc.style.top = rect.top + "px";
        pc.style.right = (window.innerWidth - rect.left + 8) + "px";
        pc.style.left = "auto";
        pc.style.bottom = "auto";
    }

    pc.classList.add("visible");
    // 重置暂停按钮状态
    const ppIcon = document.getElementById("btn-play-pause")?.querySelector(".icon");
    const ppLabel = document.getElementById("btn-play-pause")?.querySelector(".label");
    if (ppIcon) ppIcon.textContent = "⏸";
    if (ppLabel) ppLabel.textContent = "暂停";
}

/**
 * @function togglePause
 * @brief 暂停/继续漫游
 */
function togglePause() {
    const state = autowalkState;
    if (!state.active) return;

    state.paused = !state.paused;

    const btn = document.getElementById("btn-play-pause");
    const icon = btn?.querySelector(".icon");
    const label = btn?.querySelector(".label");
    if (icon) icon.textContent = state.paused ? "▶" : "⏸";
    if (label) label.textContent = state.paused ? "继续" : "暂停";

    if (!state.paused) {
        // 继续 - 重新开始动画
        if (!state.waiting && !state.animFrame) {
            const nodeIdx = state.nodeIdx;
            const nextIdx = nodeIdx + 1;
            if (nextIdx < state.nodes.length) {
                const segPts = getSegmentRoutePoints(state.routePts, nodeIdx, nextIdx);
                animateMovement(segPts, 0);
            }
        }
    }
}

/**
 * @function skipToNext
 * @brief 跳至下一节点
 */
function skipToNext() {
    const state = autowalkState;
    if (!state.active) return;

    // 清除当前动画
    if (state.animFrame) {
        clearTimeout(state.animFrame);
        state.animFrame = null;
    }
    if (state.waitTimer) {
        clearTimeout(state.waitTimer);
        state.waitTimer = null;
    }
    state.waiting = false;

    const nextIdx = state.nodeIdx + 1;
    if (nextIdx >= state.nodes.length) {
        alert("已到达终点！");
        stopAutowalk();
        return;
    }

    // 直接跳到下一个节点
    const nextNode = state.nodes[nextIdx];
    arriveAtNode(nextIdx);
}

/**
 * @function restartAutowalk
 * @brief 重头开始
 */
function restartAutowalk() {
    if (!autowalkState.active) return;

    // 清除状态
    if (autowalkState.animFrame) {
        clearTimeout(autowalkState.animFrame);
        autowalkState.animFrame = null;
    }
    if (autowalkState.waitTimer) {
        clearTimeout(autowalkState.waitTimer);
        autowalkState.waitTimer = null;
    }
    if (autowalkState.marker) {
        map.instance.removeLayer(autowalkState.marker);
    }

    closeNodePanel();

    // 重置并重新开始
    const army = autowalkState.army;
    const speed = autowalkState.speed;

    autowalkState = {
        active: false, paused: false, speed: speed, army: army,
        nodes: [], routePts: [], nodeIdx: 0,
        segStart: null, segEnd: null, segDuration: speed * 1000,
        animFrame: null, animStart: null, marker: null,
        waiting: false, waitTimer: null,
    };

    document.getElementById("autowalk-label").textContent = "漫游";

    setTimeout(() => {
        if (typeof setAutowalkSpeed === "function") {
            showSpeedSelector();
        }
    }, 300);
}

/**
 * @function stopAutowalk
 * @brief 停止自动漫游
 */
function stopAutowalk() {
    if (autowalkState.animFrame) {
        clearTimeout(autowalkState.animFrame);
        autowalkState.animFrame = null;
    }
    if (autowalkState.waitTimer) {
        clearTimeout(autowalkState.waitTimer);
        autowalkState.waitTimer = null;
    }
    if (autowalkState.marker) {
        try { map.instance.removeLayer(autowalkState.marker); } catch(e) {}
        autowalkState.marker = null;
    }

    closeNodePanel();
    hideAutowalkStatus();

    autowalkState.active = false;
    autowalkState.paused = false;

    document.getElementById("autowalk-label").textContent = "漫游";
    document.getElementById("speed-selector")?.classList.remove("visible");
    document.getElementById("play-controls")?.classList.remove("visible");

    setActiveControl(null);
    console.log("[Autowalk] 已停止");
}

// ============================================================================
// 进度显示
// ============================================================================

/**
 * @function showAutowalkStatus
 * @brief 显示自动漫游状态栏
 * @param {number} totalNodes 总节点数
 */
function showAutowalkStatus(totalNodes) {
    const el = document.getElementById("autowalk-status");
    if (!el) return;
    el.querySelector(".army-name").textContent = (armyNames[autowalkState.army] || "长征路线") + " 漫游中";
    el.querySelector(".progress-bar").style.width = "0%";
    el.querySelector(".segment-info").textContent = `1 / ${totalNodes}`;
    el.classList.add("visible");
}

/**
 * @function updateAutowalkProgress
 * @brief 更新自动漫游进度
 * @param {number} nodeIdx  当前到达的节点索引
 * @param {number} total    总节点数
 * @param {number} progress 段内进度 0~1
 */
function updateAutowalkProgress(nodeIdx, total, progress) {
    const el = document.getElementById("autowalk-status");
    if (!el) return;
    // 整体进度 = (当前节点索引 + 段内进度) / 总节点数
    const pct = ((nodeIdx + progress) / Math.max(total - 1, 1)) * 100;
    el.querySelector(".progress-bar").style.width = `${Math.min(pct, 100)}%`;
    el.querySelector(".segment-info").textContent = `${nodeIdx + 1} / ${total}`;
    const node = autowalkState.nodes[nodeIdx];
    el.querySelector(".current-title").textContent = node ? node.title : "";
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
 * @brief 显示/隐藏军队选择器（紧靠按钮左侧展开）
 */
function toggleArmySelector() {
    const el = document.getElementById("army-selector");
    if (!el) return;

    if (el.classList.contains("visible")) {
        el.classList.remove("visible");
        return;
    }

    // 定位到军队按钮的左侧
    const btn = document.getElementById("btn-army");
    if (btn) {
        const rect = btn.getBoundingClientRect();
        // 出现在按钮左侧 8px 位置，垂直对齐
        el.style.top = rect.top + "px";
        el.style.right = (window.innerWidth - rect.left + 8) + "px";
        el.style.left = "auto";
        el.style.bottom = "auto";
    }

    el.classList.add("visible");

    // 点击外部关闭选择器
    setTimeout(() => {
        document.addEventListener("click", closeArmySelector);
    }, 0);
}

/**
 * @function closeArmySelector
 * @brief 点击军队选择器外部时关闭
 * @param {Event} e 点击事件
 */
function closeArmySelector(e) {
    const el = document.getElementById("army-selector");
    const btn = document.getElementById("btn-army");
    if (!el || !btn) return;
    if (!el.contains(e.target) && !btn.contains(e.target)) {
        el.classList.remove("visible");
        document.removeEventListener("click", closeArmySelector);
    }
}

/**
 * @function selectArmy
 * @brief 选择军队并更新路线显示
 * @param {number} army 军队编号
 */
function selectArmy(army) {
    autowalkState.army = army;
    document.querySelectorAll(".army-item").forEach(item => {
        item.classList.toggle("active", parseInt(item.dataset.army) === army);
    });
    toggleArmy(army);
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
    if (messageBoardOpen) loadMessages();
}

/**
 * @function loadMessages
 * @brief 加载留言数据
 */
function loadMessages() {
    const list = document.querySelector(".message-list");
    if (!list) return;
    list.innerHTML = `
        <div class="message-item">
            <span class="msg-user">游客张三</span>
            <span class="msg-time">2026-07-15</span>
            <div style="margin-top:4px">瑞金，长征的起点！</div>
        </div>
        <div class="message-item">
            <span class="msg-user">历史爱好者</span>
            <span class="msg-time">2026-07-14</span>
            <div style="margin-top:4px">湘江战役是长征途中最惨烈的战役之一</div>
        </div>`;
}

/**
 * @function sendMessage
 * @brief 发送留言
 */
function sendMessage() {
    const input = document.querySelector(".message-input-row input");
    const text = input?.value.trim();
    if (!text) return;
    console.log("[Message] 发送:", text);
    input.value = "";
    const list = document.querySelector(".message-list");
    if (list) {
        const now = new Date().toLocaleDateString("zh-CN");
        list.innerHTML = `<div class="message-item">
            <span class="msg-user">我</span>
            <span class="msg-time">${now}</span>
            <div style="margin-top:4px">${escapeHtml(text)}</div>
        </div>` + list.innerHTML;
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

/**
 * @function fetchContentForTTS
 * @brief 获取节点全部内容用于 TTS 朗读（包括所有字段，不只是面板显示的内容）
 * @param {string} nodeId  节点ID
 * @param {function} onDone  语音完成后回调
 */
async function fetchContentForTTS(nodeId, onDone) {
    try {
        const resp = await fetch(`/api/v1/nodes/${nodeId}`);
        const json = await resp.json();
        if (json.code !== 0 || !json.data) {
            if (onDone) onDone();
            return;
        }
        const nd = json.data;

        // 收集所有有内容的字段（不局限于面板显示的8项）
        const allFields = [
            { key: "famous_battle", label: "著名战役" },
            { key: "important_meeting", label: "重要会议" },
            { key: "history_event", label: "历史事件" },
            { key: "core_site", label: "核心遗址" },
            { key: "poem_article", label: "诗词文章" },
            { key: "typical_story", label: "典型故事" },
            { key: "typical_people", label: "典型人物" },
            { key: "historical_significance", label: "历史意义" },
            { key: "spark_remains", label: "星火遗存" },
        ];

        let texts = [];
        allFields.forEach(f => {
            const val = nd[f.key];
            if (val && typeof val === "string" && val.trim() && val.trim() !== "无" && val.trim().indexOf("无。") !== 0) {
                texts.push(f.label + "：" + val);
            }
        });

        if (texts.length > 0) {
            speakText(texts.join("。"));
        }

        if (onDone) {
            // 检查语音何时结束（每隔500ms检查）
            const speechCheck = setInterval(() => {
                if (!window.speechSynthesis || !window.speechSynthesis.speaking) {
                    clearInterval(speechCheck);
                    onDone();
                }
            }, 500);
        }
    } catch (e) {
        console.error("[TTS] 获取内容失败:", e);
        if (onDone) onDone();
    }
}

/**
 * @function checkSpeechDone
 * @brief 轮询检查语音是否朗读完毕
 * @param {number} interval 检查间隔（ms），默认 1000
 */
function checkSpeechDone(interval) {
    if (!interval) interval = 1000;
    if (!autowalkState.active || !autowalkState.waiting) return;

    if (!window.speechSynthesis || !window.speechSynthesis.speaking) {
        autowalkState.waiting = false;
        moveToNextSegment();
        return;
    }

    setTimeout(() => checkSpeechDone(interval), interval);
}

// 导出
window.initControls   = initControls;
window.startAutowalk  = startAutowalk;
window.stopAutowalk   = stopAutowalk;
window.selectArmy     = selectArmy;
window.toggleMessageBoard = toggleMessageBoard;
window.sendMessage    = sendMessage;
window.selectAutowalkSpeed = selectAutowalkSpeed;
window.jumpAutowalkToNode = jumpAutowalkToNode;

/**
 * @function jumpAutowalkToNode
 * @brief 漫游中点击节点，跳转到该节点继续漫游
 * @param {string} nodeId  节点编号
 */
function jumpAutowalkToNode(nodeId) {
    var state = autowalkState;
    if (!state.active) return;

    var newIdx = -1;
    for (var i = 0; i < state.nodes.length; i++) {
        if (state.nodes[i].node_id === nodeId) {
            newIdx = i;
            break;
        }
    }
    if (newIdx < 0) return;

    if (state.animFrame) {
        clearTimeout(state.animFrame);
        state.animFrame = null;
    }
    if (state.waitTimer) {
        clearTimeout(state.waitTimer);
        state.waitTimer = null;
    }
    state.waiting = false;

    var targetNode = state.nodes[newIdx];
    if (state.marker) {
        state.marker.setLatLng([targetNode.lat, targetNode.lng]);
    }
    arriveAtNode(newIdx);
}