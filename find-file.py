from pymediainfo import MediaInfo


        file_path = self.find_file("E:\\", new_title)
        if file_path:
            title, author = self.extract_media_info(file_path)
            print(f"Title: {title}")
            print(f"Author: {author}")
            

    # Method to search for a file and stop after the first result
    def find_file(self, path, filename):
        for root, dirs, files in os.walk(path):
            if filename in files:
                return os.path.join(root, filename)
        return None

    # Method to extract title and author from MP4 file using MediaInfo
    def extract_media_info(self, file_path):
        media_info = MediaInfo.parse(file_path)
        
        title = 'Unknown'
        author = 'Unknown'
    
        for track in media_info.tracks:
            track_data = track.to_data()
            
            if track_data["track_type"] == "General":
                title = track_data.get('title', 'Unknown')
                author = track_data.get('performer', 'Unknown')

        return title, author