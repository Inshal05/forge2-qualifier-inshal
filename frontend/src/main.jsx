import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { CalendarClock, Check, Plus, Tag, Trash2, UserRound } from 'lucide-react';
import './styles.css';

const today = new Date().toISOString().slice(0, 10);

const seedBoard = {
  id: 'board-1',
  name: 'Forge 2 Qualifier',
  members: [
    { id: 'member-1', name: 'Daniyal' },
    { id: 'member-2', name: 'Hermes' },
    { id: 'member-3', name: 'OpenClaw' }
  ],
  lists: [
    {
      id: 'list-todo',
      title: 'To Do',
      cards: [
        {
          id: 'card-1',
          title: 'Wire Slack round trip',
          description: 'Capture auth.test, postMessage and conversations.history output.',
          assigneeId: 'member-1',
          dueDate: today,
          tags: [{ name: 'evidence', color: '#2f7dd1' }]
        }
      ]
    },
    {
      id: 'list-doing',
      title: 'Doing',
      cards: [
        {
          id: 'card-2',
          title: 'Kanban board UI',
          description: 'Create cards, edit details, labels, members, due dates and movement.',
          assigneeId: 'member-2',
          dueDate: '',
          tags: [{ name: 'frontend', color: '#0f9d72' }]
        }
      ]
    },
    {
      id: 'list-done',
      title: 'Done',
      cards: [
        {
          id: 'card-3',
          title: 'Hermes status skill',
          description: 'Reusable skill committed at skills/status-report/SKILL.md.',
          assigneeId: 'member-3',
          dueDate: '',
          tags: [{ name: 'agent', color: '#b25a2b' }]
        }
      ]
    }
  ]
};

const colors = ['#2f7dd1', '#0f9d72', '#b25a2b', '#8b5cf6', '#c2410c'];

function loadBoard() {
  const saved = localStorage.getItem('forge2-kanban-board');
  return saved ? JSON.parse(saved) : seedBoard;
}

function saveBoard(board) {
  localStorage.setItem('forge2-kanban-board', JSON.stringify(board));
}

function App() {
  const [board, setBoard] = useState(loadBoard);
  const [selectedId, setSelectedId] = useState('card-2');
  const [newCard, setNewCard] = useState('');
  const [newMember, setNewMember] = useState('');

  const selectedCard = useMemo(() => {
    for (const list of board.lists) {
      const card = list.cards.find((item) => item.id === selectedId);
      if (card) return { ...card, listId: list.id };
    }
    return null;
  }, [board, selectedId]);

  const updateBoard = (updater) => {
    setBoard((current) => {
      const next = updater(current);
      saveBoard(next);
      return next;
    });
  };

  const updateCard = (cardId, patch) => {
    updateBoard((current) => ({
      ...current,
      lists: current.lists.map((list) => ({
        ...list,
        cards: list.cards.map((card) => (card.id === cardId ? { ...card, ...patch } : card))
      }))
    }));
  };

  const addCard = (listId) => {
    const title = newCard.trim();
    if (!title) return;
    const card = {
      id: crypto.randomUUID(),
      title,
      description: '',
      assigneeId: '',
      dueDate: '',
      tags: []
    };
    updateBoard((current) => ({
      ...current,
      lists: current.lists.map((list) =>
        list.id === listId ? { ...list, cards: [...list.cards, card] } : list
      )
    }));
    setSelectedId(card.id);
    setNewCard('');
  };

  const moveCard = (cardId, targetListId) => {
    let movingCard = null;
    const stripped = board.lists.map((list) => ({
      ...list,
      cards: list.cards.filter((card) => {
        if (card.id === cardId) movingCard = card;
        return card.id !== cardId;
      })
    }));
    if (!movingCard) return;
    updateBoard((current) => ({
      ...current,
      lists: stripped.map((list) =>
        list.id === targetListId ? { ...list, cards: [...list.cards, movingCard] } : list
      )
    }));
  };

  const addTag = (card) => {
    const name = window.prompt('Tag name');
    if (!name) return;
    const color = colors[card.tags.length % colors.length];
    updateCard(card.id, { tags: [...card.tags, { name, color }] });
  };

  const addMember = () => {
    const name = newMember.trim();
    if (!name) return;
    updateBoard((current) => ({
      ...current,
      members: [...current.members, { id: crypto.randomUUID(), name }]
    }));
    setNewMember('');
  };

  const deleteCard = (cardId) => {
    updateBoard((current) => ({
      ...current,
      lists: current.lists.map((list) => ({
        ...list,
        cards: list.cards.filter((card) => card.id !== cardId)
      }))
    }));
    setSelectedId('');
  };

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Forge 2 Qualifier</p>
          <h1>{board.name}</h1>
        </div>
        <div className="member-add">
          <input value={newMember} onChange={(event) => setNewMember(event.target.value)} placeholder="Add member" />
          <button onClick={addMember} title="Add member"><Plus size={18} /></button>
        </div>
      </header>

      <section className="workspace">
        <div className="board">
          {board.lists.map((list) => (
            <section className="list" key={list.id}>
              <div className="list-head">
                <h2>{list.title}</h2>
                <span>{list.cards.length}</span>
              </div>
              <div className="cards">
                {list.cards.map((card) => {
                  const assignee = board.members.find((member) => member.id === card.assigneeId);
                  const overdue = card.dueDate && card.dueDate < today && list.id !== 'list-done';
                  return (
                    <button
                      className={`card ${selectedId === card.id ? 'selected' : ''} ${overdue ? 'overdue' : ''}`}
                      key={card.id}
                      onClick={() => setSelectedId(card.id)}
                    >
                      <strong>{card.title}</strong>
                      <p>{card.description || 'No description yet'}</p>
                      <div className="tag-row">
                        {card.tags.map((tagItem) => (
                          <span style={{ background: tagItem.color }} key={`${card.id}-${tagItem.name}`}>{tagItem.name}</span>
                        ))}
                      </div>
                      <div className="meta-row">
                        <span><UserRound size={14} />{assignee?.name || 'Unassigned'}</span>
                        {card.dueDate && <span><CalendarClock size={14} />{card.dueDate}</span>}
                      </div>
                    </button>
                  );
                })}
              </div>
              <form className="add-card" onSubmit={(event) => { event.preventDefault(); addCard(list.id); }}>
                <input value={newCard} onChange={(event) => setNewCard(event.target.value)} placeholder={`New card in ${list.title}`} />
                <button title="Create card"><Plus size={18} /></button>
              </form>
            </section>
          ))}
        </div>

        <aside className="details">
          {selectedCard ? (
            <>
              <div className="details-head">
                <h2>Card Details</h2>
                <button className="ghost danger" onClick={() => deleteCard(selectedCard.id)} title="Delete card"><Trash2 size={18} /></button>
              </div>
              <label>Title
                <input value={selectedCard.title} onChange={(event) => updateCard(selectedCard.id, { title: event.target.value })} />
              </label>
              <label>Description
                <textarea value={selectedCard.description} onChange={(event) => updateCard(selectedCard.id, { description: event.target.value })} />
              </label>
              <label>List
                <select value={selectedCard.listId} onChange={(event) => moveCard(selectedCard.id, event.target.value)}>
                  {board.lists.map((list) => <option value={list.id} key={list.id}>{list.title}</option>)}
                </select>
              </label>
              <label>Assignee
                <select value={selectedCard.assigneeId} onChange={(event) => updateCard(selectedCard.id, { assigneeId: event.target.value })}>
                  <option value="">Unassigned</option>
                  {board.members.map((member) => <option value={member.id} key={member.id}>{member.name}</option>)}
                </select>
              </label>
              <label>Due date
                <input type="date" value={selectedCard.dueDate} onChange={(event) => updateCard(selectedCard.id, { dueDate: event.target.value })} />
              </label>
              <div className="detail-tags">
                <div className="tag-row">
                  {selectedCard.tags.map((tagItem) => <span style={{ background: tagItem.color }} key={tagItem.name}>{tagItem.name}</span>)}
                </div>
                <button className="ghost" onClick={() => addTag(selectedCard)}><Tag size={16} /> Add tag</button>
              </div>
              <div className="saved"><Check size={16} /> Saved locally</div>
            </>
          ) : (
            <p className="empty">Select a card to edit details.</p>
          )}
        </aside>
      </section>
    </main>
  );
}

createRoot(document.getElementById('root')).render(<App />);
