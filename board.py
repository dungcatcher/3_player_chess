class Board:
    def __init__(self):
        """
        Board is represented as a list of 2d arrays of the 3 8x4 segments
        """
        self.position = [
            [  # White segment
                [None, None, None, "wr", None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"]
            ],
            [  # Black segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"]
            ],
            [  # Red segment
                [None, None, None, None, None, None, None, None],
                [None, None, None, None, None, None, None, None],
                ["rp", "rp", "rp", "rp", "rp", "rp", "rp", "rp"],
                ["rr", "rn", "rb", "rq", "rk", "rb", "rn", "rr"]
            ]
        ]
