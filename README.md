# AlfredPlugin
AlfredPlugin

Next Todo:

1. 添加分词搜索功能
2. 添加拼音搜索纠正
3. 优化icon搜索逻辑:尽可能准确的搜索ICON，如果找不到就拿Domain的Icon；批量查询ICON信息，优化DB查询
4. 历史记录，拼音搜索支持
5. 添加依靠相似度，做相关的排序

book_mark_time=19.1049804688,history_time=154.168945312,merge_time=0.064208984375
这个查询历史记录的时间需要优化

如果图片都已经找到 那么就不要去创建DB链接，目前时间大部分花在拷贝文件上；
需要将响应时间 放到 200ms 之内（最好是能够在150ms）