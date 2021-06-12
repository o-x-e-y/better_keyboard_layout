class Layout:
    def __init__(self, top_row: str, homerow: str, bottom_row: str):
        self.layout = [list(top_row), list(homerow), list(bottom_row)]
        self.fingers = [[top_row[0] + homerow[0] + bottom_row[0]],
                        [top_row[1] + homerow[1] + bottom_row[1]],
                        [top_row[2] + homerow[2] + bottom_row[2]],
                        top_row[3:5] + homerow[3:5] + bottom_row[3:5],
                        top_row[5:7] + homerow[5:7] + bottom_row[5:7],
                        [top_row[7] + homerow[7] + bottom_row[7]],
                        [top_row[8] + homerow[8] + bottom_row[8]],
                        [top_row[9] + homerow[9] + bottom_row[9]]]
