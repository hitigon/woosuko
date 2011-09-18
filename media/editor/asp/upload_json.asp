<%@ CODEPAGE=65001 %>
<% Option Explicit %>
<% Response.CodePage=65001 %>
<% Response.Charset="UTF-8" %>
<!--#include file="upload_5xsoft.inc"-->
<!--#include file="JSON_2.0.4.asp"-->
<%

' KindEditor ASP
'
' 本ASP程序是演示程序，建议不要直接在实际项目中使用。
' 如果您确定直接使用本程序，使用之前请仔细确认相关安全设置。
'

Dim aspUrl, savePath, saveUrl, maxSize, fileName, fileExt, newFileName, filePath, fileUrl, dirName
Dim extStr, imageExtStr, flashExtStr, mediaExtStr, fileExtStr
Dim upload, file, fso, ranNum, hash, ymd, mm, dd

aspUrl = Request.ServerVariables("SCRIPT_NAME")
aspUrl = left(aspUrl, InStrRev(aspUrl, "/"))

'文件保存目录路径
savePath = "../attached/"
'文件保存目录URL
saveUrl = aspUrl & "../attached/"
'定义允许上传的文件扩展名
imageExtStr = "gif,jpg,jpeg,png,bmp"
flashExtStr = "swf,flv"
mediaExtStr = "swf,flv,mp3,wav,wma,wmv,mid,avi,mpg,asf,rm,rmvb"
fileExtStr = "doc,docx,xls,xlsx,ppt,htm,html,txt,zip,rar,gz,bz2"
'最大文件大小
maxSize = 1000000

Set upload = new upload_5xsoft
Set file = upload.file("imgFile")

If file.fileSize < 1 Then
	Set upload = nothing
	Set file = nothing
	showError("请选择文件。")
End If

Set fso = Server.CreateObject("Scripting.FileSystemObject")
If Not fso.FolderExists(Server.mappath(savePath)) Then
	Set upload = nothing
	Set file = nothing
	showError("上传目录不存在。")
End If

If file.fileSize > maxSize Then
	Set upload = nothing
	Set file = nothing
	showError("上传文件大小超过限制。")
End If


dirName = Request.QueryString("dir")
If isEmpty(dirName) Then
	dirName = "image"
End If
If instr(lcase("image,flash,media,file"), dirName) < 1 Then
	showError("目录名不正确。")
End If

fileName = file.filename
fileExt = mid(fileName, InStrRev(fileName, ".") + 1)

Select Case dirName
	Case "flash" extStr = flashExtStr
	Case "media" extStr = mediaExtStr
	Case "file" extStr = fileExtStr
	Case Else  extStr = imageExtStr
End Select

If instr(extStr, lcase(fileExt)) < 1 Then
	Set upload = nothing
	Set file = nothing
	showError("上传文件扩展名是不允许的扩展名。" & chr(10) & "只允许" & extStr & "格式。")
End If

'创建文件夹
savePath = savePath & dirName & "/"
saveUrl = saveUrl & dirName & "/"
If Not fso.FolderExists(Server.mappath(savePath)) Then
	fso.CreateFolder(Server.mappath(savePath))
End If
mm = month(now)
If mm < 10 Then
	mm = "0" & mm
End If
dd = day(now)
If dd < 10 Then
	dd = "0" & dd
End If
ymd = year(now) & mm & dd
savePath = savePath & ymd & "/"
saveUrl = saveUrl & ymd & "/"
If Not fso.FolderExists(Server.mappath(savePath)) Then
	fso.CreateFolder(Server.mappath(savePath))
End If

randomize
ranNum = int(9000000 * rnd) + 10000
newFileName = year(now) & mm & dd & hour(now) & minute(now) & second(now) & ranNum & "." & fileExt

filePath = Server.mappath(savePath & newFileName)
fileUrl = saveUrl & newFileName

file.saveAs filePath

Set upload = nothing
Set file = nothing

If Not fso.FileExists(filePath) Then
	showError("上传文件失败。")
End If

Response.AddHeader "Content-Type", "text/html; charset=UTF-8"
Set hash = jsObject()
hash("error") = 0
hash("url") = fileUrl
hash.Flush
Response.End

Function showError(message)
	Response.AddHeader "Content-Type", "text/html; charset=UTF-8"
	Dim hash
	Set hash = jsObject()
	hash("error") = 1
	hash("message") = message
	hash.Flush
	Response.End
End Function
%>
