<?php
 

if(isset($_GET['id']) )
{
	$youtube_id = $_GET['id'];

	$youtube_video_info = file_get_contents('http://www.youtube.com/get_video_info?html5=1&video_id='.$youtube_id);

	echo $youtube_video_info;
}

?>
