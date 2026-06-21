<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Board;
use App\Models\Card;
use App\Models\KanbanList;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class BoardController extends Controller
{
    public function index(): JsonResponse
    {
        return response()->json(Board::with('members', 'lists.cards.tags', 'lists.cards.member')->get());
    }

    public function store(Request $request): JsonResponse
    {
        $board = Board::create($request->validate(['name' => ['required', 'string', 'max:120']]));

        foreach (['To Do', 'Doing', 'Done'] as $position => $title) {
            $board->lists()->create(['title' => $title, 'position' => $position]);
        }

        return response()->json($board->load('members', 'lists.cards.tags'), 201);
    }

    public function show(Board $board): JsonResponse
    {
        return response()->json($board->load('members', 'lists.cards.tags', 'lists.cards.member'));
    }

    public function update(Request $request, Board $board): JsonResponse
    {
        $board->update($request->validate(['name' => ['required', 'string', 'max:120']]));

        return response()->json($board->fresh()->load('members', 'lists.cards.tags'));
    }

    public function destroy(Board $board): JsonResponse
    {
        $board->delete();

        return response()->json(['deleted' => true]);
    }

    public function storeList(Request $request, Board $board): JsonResponse
    {
        $data = $request->validate(['title' => ['required', 'string', 'max:80']]);
        $data['position'] = $board->lists()->count();

        return response()->json($board->lists()->create($data), 201);
    }

    public function storeMember(Request $request, Board $board): JsonResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:80'],
            'email' => ['nullable', 'email', 'max:120'],
        ]);

        return response()->json($board->members()->create($data), 201);
    }

    public function storeCard(Request $request, KanbanList $kanbanList): JsonResponse
    {
        $data = $request->validate([
            'title' => ['required', 'string', 'max:160'],
            'description' => ['nullable', 'string'],
            'member_id' => ['nullable', 'exists:members,id'],
            'due_date' => ['nullable', 'date'],
        ]);
        $data['position'] = $kanbanList->cards()->count();

        return response()->json($kanbanList->cards()->create($data)->load('member', 'tags'), 201);
    }

    public function updateCard(Request $request, Card $card): JsonResponse
    {
        $card->update($request->validate([
            'title' => ['required', 'string', 'max:160'],
            'description' => ['nullable', 'string'],
            'member_id' => ['nullable', 'exists:members,id'],
            'due_date' => ['nullable', 'date'],
        ]));

        return response()->json($card->fresh()->load('member', 'tags'));
    }

    public function moveCard(Request $request, Card $card): JsonResponse
    {
        $data = $request->validate([
            'list_id' => ['required', 'exists:kanban_lists,id'],
            'position' => ['nullable', 'integer', 'min:0'],
        ]);

        $card->update([
            'list_id' => $data['list_id'],
            'position' => $data['position'] ?? Card::where('list_id', $data['list_id'])->count(),
        ]);

        return response()->json($card->fresh()->load('member', 'tags'));
    }

    public function storeTag(Request $request, Card $card): JsonResponse
    {
        $data = $request->validate([
            'name' => ['required', 'string', 'max:40'],
            'color' => ['required', 'string', 'max:20'],
        ]);

        return response()->json($card->tags()->create($data), 201);
    }
}
