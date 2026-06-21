<?php

use App\Http\Controllers\Api\BoardController;
use Illuminate\Support\Facades\Route;

Route::get('/boards', [BoardController::class, 'index']);
Route::post('/boards', [BoardController::class, 'store']);
Route::get('/boards/{board}', [BoardController::class, 'show']);
Route::put('/boards/{board}', [BoardController::class, 'update']);
Route::delete('/boards/{board}', [BoardController::class, 'destroy']);

Route::post('/boards/{board}/lists', [BoardController::class, 'storeList']);
Route::post('/boards/{board}/members', [BoardController::class, 'storeMember']);
Route::post('/lists/{kanbanList}/cards', [BoardController::class, 'storeCard']);
Route::put('/cards/{card}', [BoardController::class, 'updateCard']);
Route::post('/cards/{card}/move', [BoardController::class, 'moveCard']);
Route::post('/cards/{card}/tags', [BoardController::class, 'storeTag']);
