/**
 * Checkers Game - Fish Edition
 * Click the octopus to play!
 */

(function() {
  // Fish pieces: 🐠 (player - tropical fish) vs 🐡 (AI - blowfish)
  const PLAYER_PIECE = '🐠';
  const PLAYER_KING = '👑🐠';
  const AI_PIECE = '🐡';
  const AI_KING = '👑🐡';

  const PLAYER = 1;
  const AI = 2;

  let board = [];
  let selectedPiece = null;
  let currentTurn = PLAYER;
  let gameOver = false;

  // Initialize the game
  function initBoard() {
    board = [];
    for (let row = 0; row < 8; row++) {
      board[row] = [];
      for (let col = 0; col < 8; col++) {
        if ((row + col) % 2 === 1) {
          if (row < 3) {
            board[row][col] = { player: AI, king: false };
          } else if (row > 4) {
            board[row][col] = { player: PLAYER, king: false };
          } else {
            board[row][col] = null;
          }
        } else {
          board[row][col] = null;
        }
      }
    }
    selectedPiece = null;
    currentTurn = PLAYER;
    gameOver = false;
  }

  // Get valid moves for a piece
  function getValidMoves(row, col, boardState = board) {
    const piece = boardState[row][col];
    if (!piece) return { moves: [], jumps: [] };

    const moves = [];
    const jumps = [];
    const directions = [];

    // Player moves up (decreasing row), AI moves down (increasing row)
    if (piece.player === PLAYER || piece.king) {
      directions.push([-1, -1], [-1, 1]);
    }
    if (piece.player === AI || piece.king) {
      directions.push([1, -1], [1, 1]);
    }

    for (const [dr, dc] of directions) {
      const newRow = row + dr;
      const newCol = col + dc;

      if (newRow >= 0 && newRow < 8 && newCol >= 0 && newCol < 8) {
        if (boardState[newRow][newCol] === null) {
          moves.push({ row: newRow, col: newCol });
        } else if (boardState[newRow][newCol].player !== piece.player) {
          // Check for jump
          const jumpRow = newRow + dr;
          const jumpCol = newCol + dc;
          if (jumpRow >= 0 && jumpRow < 8 && jumpCol >= 0 && jumpCol < 8) {
            if (boardState[jumpRow][jumpCol] === null) {
              jumps.push({ row: jumpRow, col: jumpCol, captured: { row: newRow, col: newCol } });
            }
          }
        }
      }
    }

    return { moves, jumps };
  }

  // Check if player has any jumps available
  function hasJumps(player, boardState = board) {
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const piece = boardState[row][col];
        if (piece && piece.player === player) {
          const { jumps } = getValidMoves(row, col, boardState);
          if (jumps.length > 0) return true;
        }
      }
    }
    return false;
  }

  // Get all possible moves for a player
  function getAllMoves(player, boardState = board) {
    const allMoves = [];
    const mustJump = hasJumps(player, boardState);

    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const piece = boardState[row][col];
        if (piece && piece.player === player) {
          const { moves, jumps } = getValidMoves(row, col, boardState);

          if (mustJump) {
            for (const jump of jumps) {
              allMoves.push({ from: { row, col }, to: jump, isJump: true });
            }
          } else {
            for (const move of moves) {
              allMoves.push({ from: { row, col }, to: move, isJump: false });
            }
          }
        }
      }
    }

    return allMoves;
  }

  // Make a move on a board state (returns new board)
  function makeMove(move, boardState) {
    const newBoard = boardState.map(row => row.map(cell => cell ? { ...cell } : null));
    const piece = { ...newBoard[move.from.row][move.from.col] };

    newBoard[move.from.row][move.from.col] = null;
    newBoard[move.to.row][move.to.col] = piece;

    if (move.isJump && move.to.captured) {
      newBoard[move.to.captured.row][move.to.captured.col] = null;
    }

    // King promotion
    if (piece.player === PLAYER && move.to.row === 0) {
      newBoard[move.to.row][move.to.col].king = true;
    }
    if (piece.player === AI && move.to.row === 7) {
      newBoard[move.to.row][move.to.col].king = true;
    }

    return newBoard;
  }

  // Execute move on actual game board
  function executeMove(fromRow, fromCol, toRow, toCol, isJump, captured) {
    const piece = board[fromRow][fromCol];
    board[fromRow][fromCol] = null;
    board[toRow][toCol] = piece;

    if (isJump && captured) {
      board[captured.row][captured.col] = null;
    }

    // King promotion
    if (piece.player === PLAYER && toRow === 0) {
      piece.king = true;
    }
    if (piece.player === AI && toRow === 7) {
      piece.king = true;
    }

    // Check for additional jumps
    if (isJump) {
      const { jumps } = getValidMoves(toRow, toCol);
      if (jumps.length > 0) {
        selectedPiece = { row: toRow, col: toCol };
        renderBoard();
        return false; // Continue turn
      }
    }

    return true; // End turn
  }

  // Count pieces for evaluation
  function evaluateBoard(boardState) {
    let score = 0;
    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const piece = boardState[row][col];
        if (piece) {
          const value = piece.king ? 3 : 1;
          if (piece.player === AI) {
            score += value;
            // Bonus for advancement
            score += row * 0.1;
          } else {
            score -= value;
            // Bonus for advancement
            score -= (7 - row) * 0.1;
          }
        }
      }
    }
    return score;
  }

  // Minimax with alpha-beta pruning
  function minimax(boardState, depth, alpha, beta, isMaximizing) {
    const moves = getAllMoves(isMaximizing ? AI : PLAYER, boardState);

    if (depth === 0 || moves.length === 0) {
      return { score: evaluateBoard(boardState), move: null };
    }

    let bestMove = null;

    if (isMaximizing) {
      let maxScore = -Infinity;
      for (const move of moves) {
        const newBoard = makeMove(move, boardState);
        const result = minimax(newBoard, depth - 1, alpha, beta, false);
        if (result.score > maxScore) {
          maxScore = result.score;
          bestMove = move;
        }
        alpha = Math.max(alpha, result.score);
        if (beta <= alpha) break;
      }
      return { score: maxScore, move: bestMove };
    } else {
      let minScore = Infinity;
      for (const move of moves) {
        const newBoard = makeMove(move, boardState);
        const result = minimax(newBoard, depth - 1, alpha, beta, true);
        if (result.score < minScore) {
          minScore = result.score;
          bestMove = move;
        }
        beta = Math.min(beta, result.score);
        if (beta <= alpha) break;
      }
      return { score: minScore, move: bestMove };
    }
  }

  // AI makes a move
  function aiMove() {
    if (gameOver) return;

    const result = minimax(board, 4, -Infinity, Infinity, true);

    if (result.move) {
      const move = result.move;
      const turnComplete = executeMove(
        move.from.row, move.from.col,
        move.to.row, move.to.col,
        move.isJump, move.to.captured
      );

      if (turnComplete) {
        currentTurn = PLAYER;
        checkWinCondition();
      } else {
        // AI has additional jumps
        setTimeout(aiMove, 500);
      }
    } else {
      // AI has no moves - player wins
      gameOver = true;
      showMessage('You win! 🎉');
    }

    renderBoard();
  }

  // Check for win condition
  function checkWinCondition() {
    const playerMoves = getAllMoves(PLAYER);
    const aiMoves = getAllMoves(AI);

    if (playerMoves.length === 0) {
      gameOver = true;
      showMessage('The blowfish wins! 🐡');
    } else if (aiMoves.length === 0) {
      gameOver = true;
      showMessage('You win! 🐠🎉');
    }
  }

  // Show message in status area
  function showMessage(msg) {
    const status = document.getElementById('checkers-status');
    if (status) status.textContent = msg;
  }

  // Handle cell click
  function handleCellClick(row, col) {
    if (gameOver || currentTurn !== PLAYER) return;

    const piece = board[row][col];
    const mustJump = hasJumps(PLAYER);

    if (selectedPiece) {
      const { moves, jumps } = getValidMoves(selectedPiece.row, selectedPiece.col);
      const validMoves = mustJump ? jumps : moves;

      const targetMove = validMoves.find(m => m.row === row && m.col === col);

      if (targetMove) {
        const isJump = mustJump;
        const turnComplete = executeMove(
          selectedPiece.row, selectedPiece.col,
          row, col,
          isJump, targetMove.captured
        );

        if (turnComplete) {
          selectedPiece = null;
          currentTurn = AI;
          renderBoard();
          checkWinCondition();

          if (!gameOver) {
            showMessage('Blowfish is thinking...');
            setTimeout(aiMove, 600);
          }
        }
        return;
      } else if (piece && piece.player === PLAYER) {
        // Select different piece (only if not in middle of multi-jump)
        if (!mustJump || getValidMoves(row, col).jumps.length > 0) {
          selectedPiece = { row, col };
        }
      } else {
        selectedPiece = null;
      }
    } else if (piece && piece.player === PLAYER) {
      const { moves, jumps } = getValidMoves(row, col);
      if (mustJump && jumps.length === 0) {
        showMessage('You must jump!');
        return;
      }
      if (moves.length > 0 || jumps.length > 0) {
        selectedPiece = { row, col };
      }
    }

    renderBoard();
  }

  // Render the board
  function renderBoard() {
    const boardEl = document.getElementById('checkers-board');
    if (!boardEl) return;

    boardEl.innerHTML = '';

    const mustJump = currentTurn === PLAYER && hasJumps(PLAYER);
    let validMoves = [];

    if (selectedPiece && currentTurn === PLAYER) {
      const { moves, jumps } = getValidMoves(selectedPiece.row, selectedPiece.col);
      validMoves = mustJump ? jumps : moves;
    }

    for (let row = 0; row < 8; row++) {
      for (let col = 0; col < 8; col++) {
        const cell = document.createElement('div');
        cell.className = 'checkers-cell';
        cell.className += (row + col) % 2 === 0 ? ' checkers-cell--light' : ' checkers-cell--dark';

        const piece = board[row][col];

        if (selectedPiece && selectedPiece.row === row && selectedPiece.col === col) {
          cell.className += ' checkers-cell--selected';
        }

        if (validMoves.some(m => m.row === row && m.col === col)) {
          cell.className += ' checkers-cell--valid';
        }

        if (piece) {
          const pieceEl = document.createElement('span');
          pieceEl.className = 'checkers-piece';
          if (piece.player === PLAYER) {
            pieceEl.textContent = piece.king ? PLAYER_KING : PLAYER_PIECE;
          } else {
            pieceEl.textContent = piece.king ? AI_KING : AI_PIECE;
          }
          cell.appendChild(pieceEl);
        }

        cell.addEventListener('click', () => handleCellClick(row, col));
        boardEl.appendChild(cell);
      }
    }

    if (!gameOver) {
      if (currentTurn === PLAYER) {
        showMessage(mustJump ? 'Your turn - you must jump!' : 'Your turn');
      }
    }
  }

  // Create modal HTML
  function createModal() {
    const modal = document.createElement('div');
    modal.id = 'checkers-modal';
    modal.className = 'checkers-modal';
    modal.innerHTML = `
      <div class="checkers-modal__content">
        <button class="checkers-modal__close" id="checkers-close">&times;</button>
        <h2 class="checkers-modal__title">🐠 Fish Checkers 🐡</h2>
        <p class="checkers-modal__subtitle">You are the tropical fish. Defeat the blowfish!</p>
        <div id="checkers-status" class="checkers-status">Your turn</div>
        <div id="checkers-board" class="checkers-board"></div>
        <button id="checkers-restart" class="checkers-restart">New Game</button>
      </div>
    `;
    document.body.appendChild(modal);

    // Close button
    document.getElementById('checkers-close').addEventListener('click', closeModal);

    // Click outside to close
    modal.addEventListener('click', (e) => {
      if (e.target === modal) closeModal();
    });

    // Restart button
    document.getElementById('checkers-restart').addEventListener('click', () => {
      initBoard();
      renderBoard();
    });

    // Escape to close
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') closeModal();
    });
  }

  function openModal() {
    let modal = document.getElementById('checkers-modal');
    if (!modal) {
      createModal();
      modal = document.getElementById('checkers-modal');
    }
    modal.classList.add('checkers-modal--open');
    initBoard();
    renderBoard();
  }

  function closeModal() {
    const modal = document.getElementById('checkers-modal');
    if (modal) {
      modal.classList.remove('checkers-modal--open');
    }
  }

  // Initialize when DOM is ready
  function init() {
    const trigger = document.getElementById('checkers-trigger');
    if (trigger) {
      trigger.addEventListener('click', openModal);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
