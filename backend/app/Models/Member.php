<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Member extends Model
{
    protected $fillable = ['board_id', 'name', 'email'];

    public function board(): BelongsTo
    {
        return $this->belongsTo(Board::class);
    }
}
