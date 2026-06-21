<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Card extends Model
{
    protected $fillable = ['list_id', 'member_id', 'title', 'description', 'due_date', 'position'];

    protected $casts = [
        'due_date' => 'date:Y-m-d',
    ];

    public function list(): BelongsTo
    {
        return $this->belongsTo(KanbanList::class, 'list_id');
    }

    public function member(): BelongsTo
    {
        return $this->belongsTo(Member::class);
    }

    public function tags(): HasMany
    {
        return $this->hasMany(Tag::class);
    }
}
