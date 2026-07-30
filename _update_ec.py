import openpyxl

wb = openpyxl.load_workbook('009 变更记录/长征文化项目EC变更跟踪表.xlsx')
ws = wb['EC变更跟踪表']

# Row mapping: Row 1=表头, Row 2=规则说明, Row 3=序号1
# 序号N -> row = N + 2
r = lambda n: n + 2

# 序号4: 已修复 - 确认关闭
ws.cell(row=r(4), column=9, value='已修复')
ws.cell(row=r(4), column=10, value='关闭')

# 序号5: 已修复 - 确认关闭
ws.cell(row=r(5), column=9, value='已修复')
ws.cell(row=r(5), column=10, value='关闭')

# 序号6: 已修复 - 确认关闭
ws.cell(row=r(6), column=9, value='已修复')
ws.cell(row=r(6), column=10, value='关闭')

# 序号7: 已修复 - 确认关闭
ws.cell(row=r(7), column=9, value='已修复')
ws.cell(row=r(7), column=10, value='关闭')

# 序号8: 无需修改 - 确认关闭
ws.cell(row=r(8), column=9, value='无需修改')
ws.cell(row=r(8), column=10, value='关闭')

# 序号9: 已修复 - 确认关闭
ws.cell(row=r(9), column=9, value='已修复')
ws.cell(row=r(9), column=10, value='关闭')

# 序号10: 已修复 - 确认关闭
ws.cell(row=r(10), column=9, value='已修复')
ws.cell(row=r(10), column=10, value='关闭')

# 序号11: PROD已修复, DEV仍待修复
ws.cell(row=r(11), column=7, value='PROD(/opt/longmarch-map/) route_point数据完整(830条), 漫游功能正常。DEV(/opt/longmarch-dev/) route_point仅149条, 缺失约80%路线坐标数据')
ws.cell(row=r(11), column=8, value='将本地完整route_point数据(830条)导出SQL, 在DEV服务器执行导入。或直接替换DEV数据库文件(先备份)')
ws.cell(row=r(11), column=9, value='待修复(DEV端)')

# 序号12: 已修复 - 确认关闭
ws.cell(row=r(12), column=9, value='已修复')
ws.cell(row=r(12), column=10, value='关闭')

# 序号13: 字体字号不一致 - 分析+方案
ws.cell(row=r(13), column=7, value='主工具栏按钮(.ctrl-btn) font-size:16px, 速度面板按钮(.speed-btn) font-size:11px, 速度标签(.speed-label) 10px, 三者分属不同CSS类, 字号相差40%, 无共享排版基线')
ws.cell(row=r(13), column=8, value='定义CSS变量--panel-font-size:15px, 三个面板统一引用该变量。.speed-btn改15px, .speed-label改13px, .speed-start-btn改15px')
ws.cell(row=r(13), column=9, value='已修复')
ws.cell(row=r(13), column=10, value='关闭')

# 序号14: 与序号10/12重复 - 关闭
ws.cell(row=r(14), column=7, value='该问题与序号10/12为同一问题, 已在序号10/12的修复中解决。index.html已加block定义, messages.html已改为独立页面, admin侧边栏已添加留言管理链接')
ws.cell(row=r(14), column=8, value='无需额外修改, 与序号10/12同案修复')
ws.cell(row=r(14), column=9, value='无需修改')
ws.cell(row=r(14), column=10, value='关闭')

# 序号15: 外网访问没有语音 - 分析方案(待实施)
ws.cell(row=r(15), column=7, value='Chrome speechSynthesis存在长期Bug(crbug.com/435233): 页面打开15-30秒后引擎休眠, 后续speak()静默失败。从页面加载到漫游触发语音通常已超过休眠阈值。speakText()内stopSpeech()->cancel()可能连带终止引擎初始化。国内网络下getVoices()异步加载中文语音耗时较长')
ws.cell(row=r(15), column=8, value='1) 用户点击开始漫游时立即触发speechSynthesis.speak("")作为首次用户手势引擎预热。2) 添加Chrome语音引擎保活: 每10秒pause()+resume()。3) 添加onerror回调检测语音失败。4) primeSpeechEngine前不先cancel')

# 序号16: 留言板弹窗被菜单挡住 - 分析方案(待实施)
ws.cell(row=r(16), column=2, value='缺陷')
ws.cell(row=r(16), column=3, value='用户提出')
ws.cell(row=r(16), column=7, value='留言板(message-board)的z-index低于主工具栏或其他弹出面板, 导致弹窗右上角被菜单遮挡')
ws.cell(row=r(16), column=8, value='将.message-board的z-index调高(如z-index: 1002, 高于其他面板), 确保层级在最上层')

wb.save('009 变更记录/长征文化项目EC变更跟踪表.xlsx')
print('EC变更跟踪表已更新完成')

# 打印最终状态
wb2 = openpyxl.load_workbook('009 变更记录/长征文化项目EC变更跟踪表.xlsx', data_only=True)
ws2 = wb2['EC变更跟踪表']
print('\n=== 最终状态 ===')
for row in ws2.iter_rows(min_row=3, max_row=25, values_only=False):
    seq = row[0].value
    status = row[8].value
    confirm = row[9].value
    desc = row[3].value
    if seq is not None:
        print(f'序号{seq}: 状态={status} | 关闭确认={confirm} | {str(desc)[:40] if desc else ""}')
