#!/usr/bin/env python3
"""
B 站字幕提取器（增强版）
支持：
1. CC 字幕（UP 主上传）- 优先使用
2. 自动生成字幕
3. Whisper 语音识别（无字幕时自动降级）
"""

import re
import json
import os
import tempfile
import subprocess
from typing import Optional, Tuple
import requests


def get_bvid_from_url(url: str) -> Optional[str]:
    """从 B 站链接提取 BV 号"""
    bvid_match = re.search(r'(BV\w{10})', url)
    if bvid_match:
        return bvid_match.group(1)
    
    if 'b23.tv' in url:
        try:
            resp = requests.head(url, allow_redirects=True, timeout=10)
            return get_bvid_from_url(resp.url)
        except:
            pass
    
    return None


def get_video_info(bvid: str) -> dict:
    """获取视频基本信息"""
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('code') == 0:
            return data.get('data', {})
    except Exception as e:
        print(f"获取视频信息失败：{e}")
    
    return {}


def get_subtitle_urls(bvid: str, cid: str) -> list:
    """获取字幕 URL 列表"""
    url = f"https://api.bilibili.com/x/player/wbi/v2?bvid={bvid}&cid={cid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Referer': 'https://www.bilibili.com'
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('code') == 0:
            subtitle_info = data.get('data', {}).get('subtitle', {})
            subtitles = subtitle_info.get('subtitles', [])
            return subtitles
    except Exception as e:
        print(f"获取字幕列表失败：{e}")
    
    return []


def download_subtitle(subtitle_url: str) -> Optional[list]:
    """下载并解析字幕文件"""
    try:
        if subtitle_url.startswith('//'):
            subtitle_url = 'https:' + subtitle_url
        
        resp = requests.get(subtitle_url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get('body', [])
    except Exception as e:
        print(f"下载字幕失败：{e}")
    
    return None


def format_subtitle_to_text(subtitle_data: list) -> str:
    """将字幕数据转换为纯文本"""
    if not subtitle_data:
        return ""
    
    texts = []
    for item in subtitle_data:
        content = item.get('content', '').strip()
        if content:
            texts.append(content)
    
    return ' '.join(texts)


def download_audio_with_ytdlp(bvid: str, temp_dir: str) -> Optional[str]:
    """使用 yt-dlp 下载音频"""
    try:
        audio_path = os.path.join(temp_dir, f'{bvid}.m4a')
        
        cmd = [
            'yt-dlp',
            '--extract-audio',
            '--audio-format', 'm4a',
            '--output', audio_path,
            '--quiet',
            '--no-warnings',
            f'https://www.bilibili.com/video/{bvid}'
        ]
        
        print(f"🎵 正在下载音频...（{bvid}）")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0 and os.path.exists(audio_path):
            return audio_path
        else:
            print(f"yt-dlp 错误：{result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        print("⏱️  音频下载超时")
        return None
    except Exception as e:
        print(f"下载音频失败：{e}")
        return None


def transcribe_with_whisper(audio_path: str, model: str = "tiny") -> Optional[str]:
    """使用 Whisper 转写音频"""
    try:
        import whisper
        
        print(f"🤖 正在用 Whisper ({model}) 转写音频...")
        print("⏳ 这可能需要几分钟，请耐心等待...")
        
        whisper_model = whisper.load_model(model)
        result = whisper_model.transcribe(audio_path, language='zh')
        
        return result.get('text', '')
    except Exception as e:
        print(f"Whisper 转写失败：{e}")
        return None


def extract_subtitle(bilibili_url: str, use_whisper: bool = True, whisper_model: str = "tiny") -> Tuple[Optional[str], Optional[str], str]:
    """
    提取 B 站视频字幕（优先 CC，无则用 Whisper）
    
    Args:
        bilibili_url: B 站视频链接
        use_whisper: 是否启用 Whisper 降级
        whisper_model: Whisper 模型 (tiny/base/small/medium/large)
    
    Returns:
        (title, subtitle_text, message)
    """
    bvid = get_bvid_from_url(bilibili_url)
    if not bvid:
        return None, None, "❌ 无法从链接中提取 BV 号，请检查链接格式"
    
    video_info = get_video_info(bvid)
    if not video_info:
        return None, None, "❌ 无法获取视频信息，视频可能不存在或已被删除"
    
    title = video_info.get('title', '未知标题')
    cid = video_info.get('cid')
    
    if not cid:
        return None, None, "❌ 无法获取视频 CID"
    
    # 1. 优先尝试 CC 字幕
    print("📋 正在检查 CC 字幕...")
    subtitles = get_subtitle_urls(bvid, str(cid))
    
    if subtitles:
        subtitle_url = None
        for sub in subtitles:
            if sub.get('lan') == 'zh-CN':
                subtitle_url = sub.get('subtitle_url')
                break
        
        if not subtitle_url and subtitles:
            subtitle_url = subtitles[0].get('subtitle_url')
        
        if subtitle_url:
            subtitle_data = download_subtitle(subtitle_url)
            if subtitle_data:
                subtitle_text = format_subtitle_to_text(subtitle_data)
                return title, subtitle_text, f"✅ 成功提取 CC 字幕（{len(subtitle_data)} 条）"
    
    # 2. 没有 CC 字幕，尝试 Whisper
    if use_whisper:
        print("⚠️  未找到 CC 字幕，准备使用 Whisper 语音识别...")
        
        temp_dir = tempfile.mkdtemp(prefix='bilibili_')
        try:
            audio_path = download_audio_with_ytdlp(bvid, temp_dir)
            if audio_path:
                subtitle_text = transcribe_with_whisper(audio_path, whisper_model)
                if subtitle_text:
                    # 清理临时文件
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                    
                    return title, subtitle_text, f"✅ Whisper 转写完成（模型：{whisper_model}）"
        finally:
            # 清理临时目录
            try:
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
            except:
                pass
        
        return None, None, "❌ Whisper 转写失败"
    
    return None, None, "⚠️ 该视频没有可用字幕（关闭了 Whisper 或转写失败）"


if __name__ == "__main__":
    test_url = input("请输入 B 站视频链接：")
    title, text, msg = extract_subtitle(test_url, use_whisper=True)
    print(f"\n{msg}")
    if title:
        print(f"标题：{title}")
    if text:
        print(f"\n前 200 字：{text[:200]}...")
