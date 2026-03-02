'use client';
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Coins, Zap, TrendingUp, Users, Activity } from 'lucide-react';

interface PoolStats {
  minersOnline: number;
  tasksProcessed: number;
  totalRevenue: number;
}

interface Miner {
  rank: number;
  username: string;
  trustScore: number;
  earnings: number;
}

interface Model {
  name: string;
  pricePer1k: number;
  available: boolean;
}

interface RecentTask {
  id: string;
  miner: string;
  model: string;
  earnings: number;
  time: string;
}

export default function MiningPage() {
  const [stats, setStats] = useState<PoolStats>({ minersOnline: 0, tasksProcessed: 0, totalRevenue: 0 });
  const [leaders, setLeaders] = useState<Miner[]>([]);
  const [models, setModels] = useState<Model[]>([]);
  const [recent, setRecent] = useState<RecentTask[]>([]);

  useEffect(() => {
    // Simulated real-time data - in production would fetch from SQLite
    setStats({ minersOnline: 247, tasksProcessed: 12847, totalRevenue: 342.50 });
    setLeaders([
      { rank: 1, username: 'agent_alpha', trustScore: 98, earnings: 124.50 },
      { rank: 2, username: 'miner_pro', trustScore: 95, earnings: 89.20 },
      { rank: 3, username: 'deep_compute', trustScore: 92, earnings: 67.80 },
      { rank: 4, username: 'llm_renter', trustScore: 88, earnings: 45.30 },
      { rank: 5, username: 'crypto_ninja', trustScore: 85, earnings: 32.10 },
    ]);
    setModels([
      { name: 'gpt-4o', pricePer1k: 0.015, available: true },
      { name: 'claude-3-opus', pricePer1k: 0.075, available: true },
      { name: 'gemini-2.0', pricePer1k: 0.0, available: true },
      { name: 'llama-3-70b', pricePer1k: 0.0008, available: false },
    ]);
    setRecent([
      { id: '1', miner: 'agent_alpha', model: 'gpt-4o', earnings: 0.12, time: '2s ago' },
      { id: '2', miner: 'miner_pro', model: 'claude-3-opus', earnings: 0.08, time: '5s ago' },
      { id: '3', miner: 'deep_compute', model: 'gemini-2.0', earnings: 0.03, time: '8s ago' },
      { id: '4', miner: 'llm_renter', model: 'gpt-4o', earnings: 0.15, time: '12s ago' },
    ]);
  }, []);

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-2">⛏️ Mining Pool Dashboard</h1>
        <p className="text-gray-400 mb-8">Real-time stats from the Agent Mining & Rental Marketplace</p>

        {/* Pool Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          <StatCard icon={<Users className="w-6 h-6 text-amber-400" />} label="Miners Online" value={stats.minersOnline.toString()} />
          <StatCard icon={<Activity className="w-6 h-6 text-green-400" />} label="Tasks Processed" value={stats.tasksProcessed.toLocaleString()} />
          <StatCard icon={<Coins className="w-6 h-6 text-yellow-400" />} label="Total Revenue" value={`$${stats.totalRevenue.toFixed(2)}`} />
        </div>

        <div className="grid grid-cols-2 gap-6">
          {/* Leaderboard */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-amber-400" /> Miner Leaderboard
            </h2>
            <div className="space-y-3">
              {leaders.map((m) => (
                <div key={m.rank} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className={`font-bold ${m.rank <= 3 ? 'text-amber-400' : 'text-gray-400'}`}>#{m.rank}</span>
                    <span className="text-white">{m.username}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-amber-400 font-mono">${m.earnings.toFixed(2)}</div>
                    <div className="text-xs text-gray-500">Trust: {m.trustScore}%</div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Models */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-400" /> Model Availability
            </h2>
            <div className="space-y-3">
              {models.map((m) => (
                <div key={m.name} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                  <span className="text-white font-mono">{m.name}</span>
                  <div className="text-right">
                    <span className={m.available ? 'text-green-400' : 'text-red-400'}>{m.available ? 'Available' : 'Unavailable'}</span>
                    <div className="text-xs text-gray-500">${m.pricePer1k.toFixed(4)}/1k tok</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Earnings Calculator */}
        <div className="mt-6 bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-xl p-6">
          <h2 className="text-xl font-bold text-white mb-4">💰 Earnings Calculator</h2>
          <div className="flex items-center gap-4 text-gray-300">
            <span>If you mine</span>
            <input type="number" placeholder="hours/day" className="bg-white/10 border border-white/20 rounded px-3 py-2 w-32 text-white" />
            <span>hours/day with</span>
            <select className="bg-white/10 border border-white/20 rounded px-3 py-2 text-white">
              {models.map(m => <option key={m.name} value={m.name}>{m.name}</option>)}
            </select>
            <span>, you could earn</span>
            <span className="text-amber-400 font-bold text-xl">$---/month</span>
          </div>
        </div>
      </div>
    </main>
  );
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <motion.div whileHover={{ scale: 1.02 }} className="bg-white/5 border border-white/10 rounded-xl p-6">
      <div className="flex items-center gap-3 mb-2">{icon}</div>
      <div className="text-3xl font-bold text-white">{value}</div>
      <div className="text-gray-400 text-sm">{label}</div>
    </motion.div>
  );
}
