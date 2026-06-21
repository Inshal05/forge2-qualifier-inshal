<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Tag extends Model
{
    protected $fillable = ['card_id', 'name', 'color'];

    public function card(): BelongsTo
    {
        return $this->belongsTo(Card::class);
    }
}
