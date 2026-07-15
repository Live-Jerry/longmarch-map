# -*- coding: utf-8 -*-
"""
@file    services/tts_service.py
@brief   语音朗读服务（TTS）
@details 提供文本转语音功能，当前实现基于 Web Speech API（浏览器端）。
             此模块主要用于生成前端 TTS 配置和语音合成参数。
@author  长征文化数字地图项目组
@date    2026-07-15
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSConfig:
    """
    @class TTSConfig
    @brief TTS 语音配置数据类
    """
    voice:       str   = "zh-CN"
    rate:        float = 0.9      # 语速 0.1 ~ 10
    pitch:       float = 1.0      # 音调 0 ~ 2
    volume:      float = 1.0      # 音量 0 ~ 1
    lang:        str   = "zh-CN"  # 语言


class TTSService:
    """
    @class TTSService
    @brief 文本转语音服务
    @details 提供前端调用的语音合成参数配置。
             实际语音合成使用浏览器内置的 Web Speech API，
             此服务提供节点内容的语音文本构建和配置参数。
    """

    # 各内容模块对应的文本字段优先级（用于自动朗读）
    CONTENT_FIELDS = [
        ("title",                   "标题"),
        ("time",                    "时间"),
        ("location",                "地点"),
        ("core_numbers",            "部队番号"),
        ("famous_battle",           "著名战役"),
        ("important_meeting",       "重要会议"),
        ("history_event",           "历史事件"),
        ("core_site",               "核心遗址"),
        ("poem_article",            "诗词文章"),
        ("typical_story",           "典型故事"),
        ("typical_people",          "典型人物"),
        ("historical_significance", "历史意义"),
        ("spark_remains",           "星火遗存"),
    ]

    @staticmethod
    def build_speech_text(node_data):
        """
        @brief  根据节点数据构建完整的语音朗读文本
        @param  node_data  节点数据字典
        @return str        合并后的朗读文本
        """
        parts = []

        # 开场白
        parts.append(f"现在来到 {node_data.get('location', '未知地点')}，")
        parts.append(f"这里是 {node_data.get('title', '历史节点')}。")

        for field, label in TTSService.CONTENT_FIELDS[2:]:
            value = node_data.get(field)
            if value and isinstance(value, str) and len(value.strip()) > 2:
                parts.append(f"{label}：{value.strip()}")

        return "\n".join(parts)

    @staticmethod
    def get_tts_config():
        """
        @brief  获取默认 TTS 配置（供前端使用）
        @return dict  TTS 配置参数
        """
        cfg = TTSConfig()
        return {
            "voice":  cfg.voice,
            "rate":   cfg.rate,
            "pitch":  cfg.pitch,
            "volume": cfg.volume,
            "lang":   cfg.lang,
            # 可用的中文语音包（浏览器各异，仅供参考）
            "supported_voices": [
                {"name": "Microsoft Yaxia (Chinese)", "lang": "zh-CN"},
                {"name": "Google 普通话",             "lang": "zh-CN"},
                {"name": "Apple XiaoMei",             "lang": "zh-CN"},
            ]
        }

    @staticmethod
    def get_node_audio_segments(node_data):
        """
        @brief  将节点内容拆分为多个朗读段落（用于分步朗读）
        @param  node_data  节点数据字典
        @return list       段落列表，每个元素含 text 和 label
        """
        segments = []

        segments.append({
            "label": "地点介绍",
            "text":  f"现在来到 {node_data.get('location', '未知地点')}，这里是 {node_data.get('title', '历史节点')}。",
        })

        for field, label in TTSService.CONTENT_FIELDS[2:]:
            value = node_data.get(field)
            if value and isinstance(value, str) and len(value.strip()) > 2:
                segments.append({
                    "label": label,
                    "text":  value.strip(),
                })

        return segments
