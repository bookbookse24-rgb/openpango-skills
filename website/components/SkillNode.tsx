// SkillNode.tsx
// Custom React Flow node for rendering an OpenPango skill tile.
// WHY: React Flow's default node appearance doesn't convey the skill type,
// I/O types, or config — a custom node makes the canvas self-documenting.

'use client';

import React, { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { SKILL_DEFINITIONS, type SkillType } from '../types/workflow';

interface SkillNodeData {
    skillType: SkillType;
    label: string;
    config: Record<string, string>;
    inputType?: string;
    outputType?: string;
    color?: string;
}

function SkillNodeComponent({ data }: NodeProps<SkillNodeData>) {
    const def = SKILL_DEFINITIONS[data.skillType];
    const color = data.color || def?.color || '#6366f1';

    return (
        <div
            className="rounded-lg shadow-lg border border-gray-600 min-w-[180px] bg-gray-900 text-white overflow-hidden"
            style={{ borderTopColor: color, borderTopWidth: '3px' }}
        >
            {/* Input handle */}
            <Handle
                type="target"
                position={Position.Top}
                className="!bg-gray-400 !w-3 !h-3 !border-2 !border-gray-900"
            />

            {/* Header */}
            <div
                className="px-3 py-2 text-sm font-bold tracking-wide flex items-center gap-2"
                style={{ backgroundColor: `${color}22` }}
            >
                <span className="text-base">{def?.icon || '⚙️'}</span>
                <span>{data.label}</span>
            </div>

            {/* Config preview */}
            <div className="px-3 py-2 space-y-1">
                {Object.entries(data.config || {})
                    .slice(0, 3)
                    .map(([key, val]) => (
                        <div key={key} className="flex items-center gap-1 text-xs">
                            <span className="text-gray-500 font-mono">{key}:</span>
                            <span className="text-gray-300 truncate max-w-[120px]">
                                {val || '—'}
                            </span>
                        </div>
                    ))}
            </div>

            {/* I/O type badges */}
            <div className="px-3 py-1.5 border-t border-gray-700 flex justify-between text-[10px] font-mono text-gray-500 uppercase">
                <span>in: {data.inputType || def?.inputType || 'any'}</span>
                <span>out: {data.outputType || def?.outputType || 'any'}</span>
            </div>

            {/* Output handle */}
            <Handle
                type="source"
                position={Position.Bottom}
                className="!bg-gray-400 !w-3 !h-3 !border-2 !border-gray-900"
            />
        </div>
    );
}

export default memo(SkillNodeComponent);
