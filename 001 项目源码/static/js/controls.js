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

// 同步到 window 供其他模块（如 map.js）检测漫游状态
window.autowalkState = autowalkState;

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
            // 未激活：如果速度选择器已显示则关闭，否则显示
            var ss = document.getElementById("speed-selector");
            if (ss && ss.classList.contains("visible")) {
                hideSpeedSelector();
                // 同时关闭漫游控制框
                var pcEl = document.getElementById("play-controls");
                if (pcEl) {
                    pcEl.classList.remove("visible");
                    pcEl.style.display = "none";
                }
                var pcb = document.getElementById("pc-backdrop");
                if (pcb) pcb.remove();
            } else {
                showSpeedSelector();
            }
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
/**
 * @function hideSpeedSelector
 * @brief 直接隐藏速度选择器
 */
function hideSpeedSelector() {
    const ss = document.getElementById("speed-selector");
    if (!ss) return;
    ss.classList.remove("visible");
    ss.style.display = "none";
    var startBtn = document.getElementById("btn-autowalk-start");
    if (startBtn) startBtn.disabled = true;
    // 移除背板
    var backdrop = document.getElementById("ss-backdrop");
    if (backdrop) backdrop.remove();
}

/**
 * @function showSpeedSelector
 * @brief 显示速度选择器（向左弹出），用户选择后开始漫游
 */
function showSpeedSelector() {
    // 先关闭已打开的面板
    hideSpeedSelector();

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

    ss.style.display = "";  // 清除 stopAutowalk 设置的 display:none
    ss.classList.add("visible");

    // 高亮当前速度
    document.querySelectorAll(".speed-btn").forEach(btn => {
        btn.classList.toggle("active", parseInt(btn.dataset.speed) === autowalkSpeed);
    });

    // 同时显示漫游控制框（让用户看到可用操作，未开始前可点外部关闭）
    if (!autowalkState.active) {
        var pcEl4 = document.getElementById("play-controls");
        if (pcEl4 && !pcEl4.classList.contains("visible")) {
            var btn4 = document.getElementById("btn-autowalk");
            if (btn4) {
                var rect4 = btn4.getBoundingClientRect();
                pcEl4.style.top = rect4.top + "px";
                pcEl4.style.right = (window.innerWidth - rect4.left + 8) + "px";
                pcEl4.style.left = "auto";
                pcEl4.style.bottom = "auto";
            }
            pcEl4.style.display = "";
            pcEl4.classList.add("visible");
            if (btn4) {
                var pcRect4 = pcEl4.getBoundingClientRect();
                ss.style.top = (pcRect4.bottom + 4) + "px";
                ss.style.right = (window.innerWidth - btn4.getBoundingClientRect().left + 8) + "px";
            }
        }
    }

    // 添加全屏背板，点击背板关闭速度选择器
    var backdrop = document.createElement("div");
    backdrop.id = "ss-backdrop";
    backdrop.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;z-index:9998;background:transparent;cursor:default;";
    backdrop.addEventListener("click", function() {
        // 漫游已开始时只有关闭按钮才能退出
        if (autowalkState.active) return;
        hideSpeedSelector();
        // 同时关闭漫游控制框
        var pcEl = document.getElementById("play-controls");
        if (pcEl) {
            pcEl.classList.remove("visible");
            pcEl.style.display = "none";
        }
        var pcb = document.getElementById("pc-backdrop");
        if (pcb) pcb.remove();
    });
    document.body.appendChild(backdrop);

    // 自动选中当前速度
    selectAutowalkSpeed(autowalkSpeed);
}



/**
 * @function setAutowalkSpeed
 * @brief 选择漫游速度并开始
 * @param {number} seconds 每节点对移动时间
 */
function selectAutowalkSpeed(seconds) {
    // 漫游进行中不能修改速度，暂停后可改
    if (autowalkState && autowalkState.active && !autowalkState.paused) return;

    autowalkSpeed = seconds;
    document.querySelectorAll(".speed-btn").forEach(btn => {
        btn.classList.toggle("active", parseInt(btn.dataset.speed) === seconds);
    });
    // 漫游中不启用"开始"按钮（防止再次点击产生重复红点）
    var startBtn = document.getElementById("btn-autowalk-start");
    if (startBtn && !autowalkState.active) {
        startBtn.disabled = false;
    }
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
    // 清理已有漫游标记和动画，防止重复点击"开始"产生多个红点
    if (autowalkState.marker) {
        try { map.instance.removeLayer(autowalkState.marker); } catch(e) {}
    }
    if (autowalkState.animFrame) {
        clearTimeout(autowalkState.animFrame);
        autowalkState.animFrame = null;
    }
    if (autowalkState.waitTimer) {
        clearTimeout(autowalkState.waitTimer);
        autowalkState.waitTimer = null;
    }

    // 速度选择弹窗与漫游控制弹窗行为保持一致，不提前关闭
    
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

    // 同步到 window 供 map.js 检测漫游状态
    window.autowalkState = autowalkState;

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

    // 启动后禁用"开始"按钮，防止再次点击（不隐藏速度选择器）
    document.getElementById("btn-autowalk-start").disabled = true;
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

    const wasAnimating = !!state.animFrame;
    // 标记动画状态（animFrame会在下面被清除）
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

    // 添加漫游控制框背板：仅漫游未开始时有效
    // 漫游中只能点退出按钮退出
    if (!document.getElementById("pc-backdrop") && !autowalkState.active) {
        var pcBd2 = document.createElement("div");
        pcBd2.id = "pc-backdrop";
        pcBd2.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;z-index:9998;background:transparent;cursor:default;";
        pcBd2.addEventListener("click", function() {
            var pEl = document.getElementById("play-controls");
            if (pEl) {
                pEl.classList.remove("visible");
                pEl.style.display = "none";
            }
            this.remove();
        });
        document.body.appendChild(pcBd2);
    }

    pc.style.display = "";  // 清除 stopAutowalk 设置的 display:none
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

    // 记录当前是否在动画中（必须先记录再清除）
    const wasAnimating = !!state.animFrame;

    // 清除当前动画/等待
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

    if (wasAnimating) {
        // 动画进行中：直接跳到目标节点（避免标记回退）
        state.nodeIdx = nextIdx;
        var tn = state.nodes[nextIdx];
        if (state.marker) {
            state.marker.setLatLng([tn.lat, tn.lng]);
            if (typeof map !== "undefined" && map.instance) {
                map.instance.panTo([tn.lat, tn.lng], { animate: true, duration: 0.5 });
            }
        }
        arriveAtNode(nextIdx);
    } else {
        // 等待中/空闲：平滑动画到下一节点
        var segPts = getSegmentRoutePoints(state.routePts, state.nodeIdx, nextIdx);
        if (segPts.length > 0) {
            animateMovement(segPts, 0);
        } else {
            arriveAtNode(nextIdx);
        }
    }
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

    // 同步到 window
    window.autowalkState = autowalkState;

    document.getElementById("autowalk-label").textContent = "漫游";

    // 直接重新开始漫游（不弹速度选择，速度面板一直可见）
    startAutowalk();
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

    // 关闭所有漫游子菜单
    hideSpeedSelector();
    var pc = document.getElementById("play-controls");
    if (pc) { pc.classList.remove("visible"); pc.style.display = "none"; }
    var bd3 = document.getElementById("pc-backdrop");
    if (bd3) bd3.remove();

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
        el.style.right = "auto";
        el.style.left = (rect.left - 210) + "px";
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
 * @function closeMessageBoard
 * @brief 关闭留言板
 */
function closeMessageBoard() {
    const el = document.getElementById("message-board");
    if (!el) return;
    messageBoardOpen = false;
    el.classList.remove("visible");
    el.style.display = "none";
    setActiveControl(null);
}

/**
 * @function toggleMessageBoard
 * @brief 显示/隐藏留言板
 */
function toggleMessageBoard() {
    const el = document.getElementById("message-board");
    if (!el) return;
    if (el.classList.contains("visible")) {
        closeMessageBoard();
        return;
    }
    messageBoardOpen = true;
    el.style.display = "";
    el.classList.add("visible");
    setActiveControl("message");
    loadMessages();
}

/**
 * @function loadMessages
 * @brief 加载留言数据
 */
function loadMessages() {
    const list = document.querySelector(".message-list");
    if (!list) return;
    // 调 API 获取留言
    fetch("/api/v1/messages")
        .then(r => r.json())
        .then(resp => {
            if (resp.code !== 0 || !resp.data) return;
            if (resp.data.length === 0) {
                list.innerHTML = "<div class=\"message-item\" style=\"color:#999\">暂无留言，来写下第一条吧</div>";
                return;
            }
            list.innerHTML = resp.data.map(function(msg) {
                var name = msg.user_name || "匿名用户";
                var time = msg.created_at || "";
                return "<div class=\"message-item\">" +
                    "<span class=\"msg-user\">" + escapeHtml(name) + "</span>" +
                    "<span class=\"msg-time\">" + escapeHtml(time) + "</span>" +
                    "<div style=\"margin-top:4px\">" + escapeHtml(msg.content) + "</div>" +
                    "</div>";
            }).join("");
        });
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
    // 调 API 提交
    fetch("/api/v1/messages", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({content: text, user_name: ""})
    }).then(function(r) { return r.json(); }).then(function(resp) {
        if (resp.code === 0) {
            loadMessages();
        }
    });
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

        // 开头朗读节点标题和时间
        const nodeTitle = nd.title || "";
        const nodeTime = nd.time || "";
        if (nodeTitle) texts.push(nodeTitle);
        if (nodeTime) texts.push(nodeTime);

        // 各内容字段
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
window.hideSpeedSelector = hideSpeedSelector;
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

    // 取路线点平滑移动到目标节点
    var segPts = getSegmentRoutePoints(state.routePts, state.nodeIdx, newIdx);
    if (!segPts || segPts.length < 2) {
        // 无路线点时直接跳
        var targetNode = state.nodes[newIdx];
        if (state.marker) {
            state.marker.setLatLng([targetNode.lat, targetNode.lng]);
            if (typeof map !== "undefined" && map.instance) {
                map.instance.panTo([targetNode.lat, targetNode.lng], { animate: true, duration: 0.5 });
            }
        }
        arriveAtNode(newIdx);
        return;
    }

    // 设置 nodeIdx 为 newIdx-1，这样 animateMovement 末尾的 arriveAtNode 会到 newIdx
    state.nodeIdx = newIdx - 1;
    animateMovement(segPts, 0);
}