# 3 Player Chess

My implementation of three-man chess with some alterations https://en.wikipedia.org/wiki/Three-man_chess
<img width="745" alt="readme image" src="https://user-images.githubusercontent.com/76923259/164628702-b412dc8f-b808-4a8f-b2cd-97ec67fe74ed.png">

## Rules:
- The turns go in anti-clockwise order (i.e white, black, red)
- A player wins when both of his opponents have been checkmated.
- When an opponent is checkmated, their pieces turn grey but stay on the board, and their turn is skipped.
- When there are still three players left, a stalemate still counts as a checkmate. If there are two players, then the game is a draw between the two remaining players.
- Pawns promote on either of the opponents' back ranks, or the furthest rank directly opposite the player.
- The diagonals are split in the centre along the two same coloured squares of the diagonal.
