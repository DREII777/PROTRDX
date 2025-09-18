"use client";

import { useEffect, useMemo, useState } from "react";
import { apiClient } from "../lib/api";

interface Ticker {
  id: number;
  symbol: string;
  market: string;
  active: boolean;
  created_at: string;
}

interface Job {
  id: number;
  started_at: string;
  finished_at?: string;
  status: string;
  summary?: string;
}

export default function Dashboard() {
  const [password, setPassword] = useState<string | null>(null);
  const [passInput, setPassInput] = useState("");
  const [tickers, setTickers] = useState<Ticker[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const client = useMemo(() => apiClient(password), [password]);

  const loadData = async () => {
    if (!password) return;
    setLoading(true);
    try {
      const [watchlistRes, jobsRes] = await Promise.all([
        client.get("/watchlist"),
        client.get("/jobs")
      ]);
      setTickers(watchlistRes.data);
      setJobs(jobsRes.data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [password]);

  const handleLogin = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setPassword(passInput);
  };

  const runPipeline = async () => {
    if (!password) return;
    try {
      await client.post("/run");
      await loadData();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="space-y-8">
      {!password ? (
        <form onSubmit={handleLogin} className="space-y-4 bg-white shadow p-6 rounded">
          <div>
            <label className="block text-sm font-medium">Admin password</label>
            <input
              type="password"
              className="mt-2 w-full border rounded px-3 py-2"
              value={passInput}
              onChange={(event) => setPassInput(event.target.value)}
            />
          </div>
          <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Unlock</button>
        </form>
      ) : (
        <>
          <section className="bg-white shadow rounded p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold">Watchlist</h2>
              <button onClick={runPipeline} className="px-3 py-2 bg-emerald-600 text-white rounded">
                Run now
              </button>
            </div>
            <p className="text-sm text-gray-500">Tickers currently monitored by the pipeline.</p>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Symbol</th>
                    <th className="text-left p-2">Market</th>
                    <th className="text-left p-2">Active</th>
                    <th className="text-left p-2">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {tickers.map((ticker) => (
                    <tr key={ticker.id} className="border-b">
                      <td className="p-2 font-semibold">{ticker.symbol}</td>
                      <td className="p-2">{ticker.market}</td>
                      <td className="p-2">{ticker.active ? "Yes" : "No"}</td>
                      <td className="p-2">{new Date(ticker.created_at).toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="bg-white shadow rounded p-6 space-y-4">
            <h2 className="text-xl font-semibold">Recent jobs</h2>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div key={job.id} className="border rounded p-3">
                    <div className="flex justify-between">
                      <span className="font-semibold">Job #{job.id}</span>
                      <span className="text-sm">{job.status}</span>
                    </div>
                    <p className="text-sm text-gray-500">
                      Started {new Date(job.started_at).toLocaleString()} · Finished {job.finished_at ? new Date(job.finished_at).toLocaleString() : "pending"}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
