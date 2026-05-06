基于pywexin和langchain的微信agentbot，其中llm我用的vllm本地部署
自动化wechat使用的是开源的pyweixin：https://github.com/evilpan/pyweixin/tree/master
可以自定义tools（我自己只加了5个tools：comfyui_api生图，操作mysql，微信发送文件信息，百度地图mcptools和麦当劳mcptools）
agent自动使用长期记忆filesaver类，保存记忆文件夹在tools/file_saver去自定义保存路径

example：

mysql_tools：mysql docker部署
<img width="1077" height="4742" alt="5" src="https://github.com/user-attachments/assets/6e3eada7-c3c4-4869-8249-cb3a420cdd37" />
<img width="1844" height="670" alt="2" src="https://github.com/user-attachments/assets/bf723e20-d62f-461d-9a0c-c5f0fce662a6" />
amap_tools：申请百度地图key后在tools/amap_tools替换
<img width="1080" height="6305" alt="4" src="https://github.com/user-attachments/assets/f3374860-3b45-4e34-844f-702508d968a2" />
picture_generate_tools：在comfyui搭建好网络后导出json，把json内容在mcp_tools/picture_generate_tools中替换
<img width="1905" height="763" alt="1" src="https://github.com/user-attachments/assets/b1561d85-158a-425a-94dc-eb95f2e55c72" />
<img width="1080" height="2400" alt="3" src="https://github.com/user-attachments/assets/4c8afc19-04d4-4149-9754-c415acc46583" />

