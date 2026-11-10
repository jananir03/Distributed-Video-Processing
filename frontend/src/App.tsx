
import { useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import {
  NavLink,
  Route,
  Routes,
  useNavigate,
  useParams,
} from 'react-router-dom';
import {
  Activity,
  ArrowDownToLine,
  ArrowLeft,
  CheckCircle2,
  Clapperboard,
  Clock3,
  CloudUpload,
  Film,
  Gauge,
  HardDrive,
  LayoutDashboard,
  RefreshCw,
  Search,
  Settings2,
  Video,
  XCircle,
} from 'lucide-react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { API_BASE, errorMessage, videoApi } from './services/api';
import type { JobItem, OutputItem, VideoItem } from './types';

type ProcessingStatus = {
  video_id?: string;
  video_status?: string;
  processing_status?: string;
  total_jobs?: number;
  completed_jobs?: number;
  failed_jobs?: number;
};

function App() {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [processingStatuses, setProcessingStatuses] = useState<
    Record<string, ProcessingStatus>
  >({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const refresh = async () => {
    try {
      setError('');

      const response = await videoApi.list();
      const videoList = response.items;

      setVideos(videoList);

      // Fetch the actual processing status for every uploaded video.
      const statusResults = await Promise.allSettled(
        videoList.map(async (video) => ({
          id: video.id,
          status: (await videoApi.status(video.id)) as ProcessingStatus,
        })),
      );

      const nextStatuses: Record<string, ProcessingStatus> = {};

      statusResults.forEach((result) => {
        if (result.status === 'fulfilled') {
          nextStatuses[result.value.id] = result.value.status;
        }
      });

      setProcessingStatuses(nextStatuses);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const stats = useMemo(() => {
    let done = 0;
    let active = 0;
    let failed = 0;

    videos.forEach((video) => {
      const processing = processingStatuses[video.id];
      const status = String(
        processing?.processing_status || video.status || '',
      ).toLowerCase();

      const totalJobs = Number(processing?.total_jobs || 0);
      const completedJobs = Number(processing?.completed_jobs || 0);
      const failedJobs = Number(processing?.failed_jobs || 0);

      if (
        /fail|error/.test(status) ||
        failedJobs > 0
      ) {
        failed += 1;
      } else if (
        /complete|success|ready/.test(status) ||
        (totalJobs > 0 && completedJobs === totalJobs)
      ) {
        done += 1;
      } else {
        // Uploaded videos with no completed processing status are active.
        active += 1;
      }
    });

    return {
      total: videos.length,
      done,
      active,
      failed,
    };
  }, [videos, processingStatuses]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Clapperboard size={21} />
          </div>
          <div>
            <b>FrameFlow</b>
            <small>VIDEO WORKSPACE</small>
          </div>
        </div>

        <div className="nav-label">WORKSPACE</div>

        <nav>
          <NavLink to="/" end>
            <LayoutDashboard size={18} />
            Overview
          </NavLink>
          <NavLink to="/library">
            <Film size={18} />
            Video library
          </NavLink>
          <NavLink to="/upload">
            <CloudUpload size={18} />
            Upload video
          </NavLink>
        </nav>

        <div className="sidebar-bottom">
          <div className="api-pill">
            <span className="pulse" />
            API gateway <b>8000</b>
          </div>

          <div className="profile">
            <div className="avatar">FF</div>
            <div>
              <b>Video Studio</b>
              <small>Local workspace</small>
            </div>
            <Settings2 size={17} />
          </div>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">DISTRIBUTED VIDEO PLATFORM</span>
            <h1>Good work starts with a clear frame.</h1>
          </div>

          <button
            className="icon-button"
            onClick={() => void refresh()}
            title="Refresh library"
          >
            <RefreshCw size={18} />
          </button>
        </header>

        {error && (
          <div className="alert error">
            <XCircle size={18} />
            <span>
              {error}. Check that the backend and API Gateway are running at{' '}
              {videoApiBase()}.
            </span>
          </div>
        )}

        <Routes>
          <Route
            path="/"
            element={
              <Dashboard
                videos={videos}
                stats={stats}
                loading={loading}
                refresh={refresh}
              />
            }
          />
          <Route
            path="/library"
            element={
              <Library
                videos={videos}
                loading={loading}
                refresh={refresh}
              />
            }
          />
          <Route
            path="/upload"
            element={<Upload onUploaded={refresh} />}
          />
          <Route
            path="/videos/:id"
            element={<Details refresh={refresh} />}
          />
          <Route
            path="*"
            element={
              <Dashboard
                videos={videos}
                stats={stats}
                loading={loading}
                refresh={refresh}
              />
            }
          />
        </Routes>

        <footer>
          FrameFlow <span>·</span> Distributed Video Processing Platform
        </footer>
      </main>
    </div>
  );
}

function videoApiBase() {
  return API_BASE;
}

function Dashboard({
  videos,
  stats,
  loading,
  refresh,
}: {
  videos: VideoItem[];
  stats: { total: number; done: number; active: number; failed: number };
  loading: boolean;
  refresh: () => Promise<void>;
}) {
  const recent = videos.slice(0, 5);

  const chart = [
    { name: 'Completed', count: stats.done },
    { name: 'Processing', count: stats.active },
    { name: 'Failed', count: stats.failed },
  ];

  return (
    <section>
      <div className="welcome-row">
        <div>
          <span className="eyebrow">YOUR CONTROL ROOM</span>
          <h2>Workspace overview</h2>
          <p className="muted">
            A simple view of your uploaded videos and processing activity.
          </p>
        </div>

        <NavLink className="button primary" to="/upload">
          <CloudUpload size={17} />
          Upload video
        </NavLink>
      </div>

      <div className="stats-grid">
        <Stat icon={<Video />} label="Total videos" value={stats.total} tone="violet" />
        <Stat
          icon={<CheckCircle2 />}
          label="Completed"
          value={stats.done}
          tone="green"
        />
        <Stat
          icon={<Activity />}
          label="In progress"
          value={stats.active}
          tone="blue"
        />
        <Stat
          icon={<XCircle />}
          label="Failed"
          value={stats.failed}
          tone="rose"
        />
      </div>

      <div className="content-grid">
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>Recent videos</h3>
              <p className="muted">Your latest uploads</p>
            </div>
            <NavLink to="/library" className="text-link">
              View library →
            </NavLink>
          </div>

          {loading ? (
            <Loading />
          ) : recent.length ? (
            <div className="video-list">
              {recent.map((video) => (
                <VideoRow key={video.id} video={video} />
              ))}
            </div>
          ) : (
            <Empty
              title="Your library is ready"
              text="Upload your first video to see it here."
            />
          )}
        </div>

        <div className="panel chart-panel">
          <div className="panel-head">
            <div>
              <h3>Processing snapshot</h3>
              <p className="muted">Based on your current library</p>
            </div>
            <Gauge size={19} className="muted" />
          </div>

          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chart}
                margin={{ top: 8, right: 4, left: -24, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#edf0f6"
                />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#7c8498' }}
                />
                <YAxis
                  allowDecimals={false}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fontSize: 11, fill: '#7c8498' }}
                />
                <Tooltip cursor={{ fill: '#f5f4fb' }} />
                <Bar
                  dataKey="count"
                  fill="#8a78d6"
                  radius={[7, 7, 0, 0]}
                  barSize={34}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="tip">
            <Clock3 size={16} />
            Processing happens asynchronously in the backend.
          </div>
        </div>
      </div>

      <div className="quick-note">
        <div className="note-icon">
          <HardDrive size={19} />
        </div>
        <div>
          <b>Your videos stay organized</b>
          <p>
            Upload, follow processing, preview thumbnails and play available
            profiles from one place.
          </p>
        </div>
      </div>

      <button className="button light" onClick={() => void refresh()}>
        <RefreshCw size={16} /> Refresh dashboard
      </button>
    </section>
  );
}

function Stat({
  icon,
  label,
  value,
  tone,
}: {
  icon: ReactNode;
  label: string;
  value: number;
  tone: string;
}) {
  return (
    <div className="stat-card">
      <div className={`stat-icon ${tone}`}>{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function Library({
  videos,
  loading,
  refresh,
}: {
  videos: VideoItem[];
  loading: boolean;
  refresh: () => Promise<void>;
}) {
  const [q, setQ] = useState('');

  const filtered = videos.filter(
    (video) =>
      (video.original_filename || '').toLowerCase().includes(q.toLowerCase()) ||
      video.id.toLowerCase().includes(q.toLowerCase()),
  );

  return (
    <section>
      <div className="welcome-row">
        <div>
          <span className="eyebrow">YOUR COLLECTION</span>
          <h2>Video library</h2>
          <p className="muted">
            Browse uploads and open a video to see its processing details.
          </p>
        </div>

        <NavLink to="/upload" className="button primary">
          <CloudUpload size={17} />
          Upload video
        </NavLink>
      </div>

      <div className="panel">
        <div className="toolbar">
          <div className="searchbox">
            <Search size={17} />
            <input
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search by filename or video ID"
            />
          </div>

          <button className="button light" onClick={() => void refresh()}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>

        {loading ? (
          <Loading />
        ) : filtered.length ? (
          <div className="video-list">
            {filtered.map((video) => (
              <VideoRow key={video.id} video={video} />
            ))}
          </div>
        ) : (
          <Empty
            title="No matching videos"
            text="Try another search or upload a new video."
          />
        )}
      </div>
    </section>
  );
}

function VideoRow({ video }: { video: VideoItem }) {
  return (
    <NavLink className="video-row" to={`/videos/${video.id}`}>
      <div className="file-icon">
        <Film size={20} />
      </div>

      <div className="video-main">
        <b>{video.original_filename || 'Untitled video'}</b>
        <small>{video.id}</small>
      </div>

      <Status value={video.status} />

      <span className="date-text">
        {video.created_at
          ? new Date(video.created_at).toLocaleDateString()
          : '—'}
      </span>

      <span className="row-arrow">↗</span>
    </NavLink>
  );
}

function Status({ value }: { value?: string }) {
  const s = (value || 'unknown').toLowerCase();

  const cls = /complete|success|ready/.test(s)
    ? 'success'
    : /fail|error/.test(s)
      ? 'danger'
      : /process|pending|upload|queued|running/.test(s)
        ? 'working'
        : 'neutral';

  return (
    <span className={`status ${cls}`}>
      <i />
      {value || 'Unknown'}
    </span>
  );
}

function Upload({
  onUploaded,
}: {
  onUploaded: () => Promise<void>;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [progress, setProgress] = useState(0);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const nav = useNavigate();

  async function submit() {
    if (!file) return;

    setBusy(true);
    setError('');
    setMessage('');

    try {
      const video = await videoApi.upload(file, setProgress);
      setMessage(`Upload complete. Video ID: ${video.id}`);
      await onUploaded();
      nav(`/videos/${video.id}`);
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section>
      <div className="welcome-row">
        <div>
          <span className="eyebrow">ADD TO YOUR LIBRARY</span>
          <h2>Upload a video</h2>
          <p className="muted">
            Choose a source video. Processing starts automatically after upload.
          </p>
        </div>
      </div>

      <div className="upload-layout">
        <div className="panel upload-panel">
          <label className="dropzone">
            <input
              type="file"
              accept="video/*,.mp4,.mov,.mkv,.avi,.webm"
              onChange={(e) => {
                setFile(e.target.files?.[0] || null);
                setError('');
              }}
            />

            <div className="upload-icon">
              <CloudUpload size={30} />
            </div>

            <h3>{file ? file.name : 'Drop your video here'}</h3>
            <p>
              {file
                ? `${(file.size / 1024 / 1024).toFixed(1)} MB · Ready to upload`
                : 'or click to browse your computer'}
            </p>
            <span className="button light">Choose video</span>
          </label>

          {busy && (
            <div className="progress-block">
              <div className="progress-label">
                <span>Uploading</span>
                <b>{progress}%</b>
              </div>
              <div className="progress-track">
                <i style={{ width: `${progress}%` }} />
              </div>
            </div>
          )}

          {error && <div className="alert error">{error}</div>}
          {message && <div className="alert success">{message}</div>}

          <button
            className="button primary full"
            disabled={!file || busy}
            onClick={() => void submit()}
          >
            {busy ? 'Uploading…' : 'Upload and start processing'}
            <ArrowDownToLine size={17} />
          </button>
        </div>

        <div className="panel info-panel">
          <div className="soft-icon">
            <Activity size={20} />
          </div>

          <h3>What happens next?</h3>

          <ol>
            <li>
              <b>Upload</b>
              <span>Your original video is stored securely.</span>
            </li>
            <li>
              <b>Process</b>
              <span>The backend creates transcoding jobs automatically.</span>
            </li>
            <li>
              <b>Deliver</b>
              <span>
                Profiles and thumbnails become available when processing
                finishes.
              </span>
            </li>
          </ol>

          <p className="small-muted">
            Supported formats and maximum file size are enforced by the backend.
          </p>
        </div>
      </div>
    </section>
  );
}

function Details({ refresh }: { refresh: () => Promise<void> }) {
  const { id = '' } = useParams();

  const [video, setVideo] = useState<VideoItem | null>(null);
  const [status, setStatus] = useState<Record<string, unknown> | null>(null);
  const [jobs, setJobs] = useState<JobItem[]>([]);
  const [outputs, setOutputs] = useState<OutputItem[]>([]);
  const [thumbs, setThumbs] = useState<unknown>(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [profile, setProfile] = useState('720p');
  const [tab, setTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  const load = async () => {
    setLoading(true);
    setError('');

    try {
      const results = await Promise.allSettled([
        videoApi.get(id),
        videoApi.status(id),
        videoApi.jobs(id),
        videoApi.outputs(id),
        videoApi.thumbnails(id),
      ]);

      if (results[0].status === 'fulfilled') {
        setVideo(results[0].value);
      } else {
        throw results[0].reason;
      }

      if (results[1].status === 'fulfilled') {
        setStatus(results[1].value);
      }

      if (results[2].status === 'fulfilled') {
        setJobs(results[2].value);
      }

      if (results[3].status === 'fulfilled') {
        setOutputs(results[3].value);
      }

      if (results[4].status === 'fulfilled') {
        setThumbs(results[4].value);
      }
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, [id]);

  async function process() {
    setBusy(true);

    try {
      await videoApi.process(id);
      await load();
      await refresh();
    } catch (e) {
      setError(errorMessage(e));
    } finally {
      setBusy(false);
    }
  }

  const profiles = Array.from(
    new Set(
      outputs
        .map((output) => String(output.profile || output.resolution || ''))
        .filter(Boolean),
    ),
  );

  const chosen = profiles.includes(profile) ? profile : profiles[0] || '720p';

  if (loading) return <Loading />;

  return (
    <section>
      <button className="back-link" onClick={() => navigate('/library')}>
        <ArrowLeft size={16} />
        Back to library
      </button>

      {error && <div className="alert error">{error}</div>}

      <div className="detail-heading">
        <div>
          <span className="eyebrow">VIDEO DETAILS</span>
          <h2>{video?.original_filename || 'Video'}</h2>
          <p className="muted id-text">{id}</p>
        </div>

        <button className="button light" onClick={() => void load()}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      <div className="detail-tabs">
        <button
          className={tab === 'overview' ? 'active' : ''}
          onClick={() => setTab('overview')}
        >
          Overview
        </button>
        <button
          className={tab === 'playback' ? 'active' : ''}
          onClick={() => setTab('playback')}
        >
          Playback
        </button>
        <button
          className={tab === 'thumbnails' ? 'active' : ''}
          onClick={() => setTab('thumbnails')}
        >
          Thumbnails
        </button>
      </div>

      {tab === 'overview' && (
        <>
          <div className="detail-grid">
            <div className="panel">
              <div className="panel-head">
                <div>
                  <h3>Processing status</h3>
                  <p className="muted">Live status from the API Gateway</p>
                </div>

                <button
                  className="button light small-button"
                  disabled={busy}
                  onClick={() => void process()}
                >
                  {busy ? 'Checking…' : 'Check processing'}
                </button>
              </div>

              <div className="status-summary">
                <Status
                  value={String(
                    status?.processing_status || video?.status || 'Unknown',
                  )}
                />
                <span>
                  {String(
                    status?.completed_jobs ??
                      jobs.filter((job) =>
                        /complete|success/i.test(job.status || ''),
                      ).length,
                  )}{' '}
                  of {String(status?.total_jobs ?? jobs.length)} jobs completed
                </span>
              </div>

              <div className="job-list">
                {jobs.length ? (
                  jobs.map((job) => (
                    <div className="job-row" key={job.id}>
                      <div>
                        <b>{job.profile || 'Transcoding job'}</b>
                        <small>{job.id}</small>
                      </div>

                      <Status value={job.status} />

                      <span className="attempts">
                        Attempt {job.attempt_count ?? 0}/
                        {job.max_attempts ?? '—'}
                      </span>
                    </div>
                  ))
                ) : (
                  <p className="muted">
                    No jobs are visible yet. Processing is triggered
                    automatically after upload.
                  </p>
                )}
              </div>
            </div>

            <div className="panel metadata-panel">
              <h3>Video information</h3>
              <Info label="File name" value={video?.original_filename} />
              <Info label="Format" value={video?.file_extension} />
              <Info
                label="File size"
                value={
                  video?.file_size_bytes
                    ? `${(video.file_size_bytes / 1024 / 1024).toFixed(2)} MB`
                    : undefined
                }
              />
              <Info label="Content type" value={video?.content_type} />
              <Info
                label="Uploaded"
                value={
                  video?.created_at
                    ? new Date(video.created_at).toLocaleString()
                    : undefined
                }
              />
              <Info label="Video status" value={video?.status} />
            </div>
          </div>
        </>
      )}

      {tab === 'playback' && (
        <div className="panel">
          <div className="panel-head">
            <div>
              <h3>Processed video</h3>
              <p className="muted">Select an available output profile.</p>
            </div>

            <select
              value={chosen}
              onChange={(e) => setProfile(e.target.value)}
            >
              {(profiles.length ? profiles : ['360p', '720p', '1080p']).map(
                (item) => (
                  <option key={item}>{item}</option>
                ),
              )}
            </select>
          </div>

          <video
            className="player"
            controls
            playsInline
            src={videoApi.streamUrl(id, chosen)}
          >
            <track kind="captions" />
          </video>

          <a
            className="button primary download-button"
            href={videoApi.downloadUrl(id, chosen)}
          >
            <ArrowDownToLine size={16} />
            Download {chosen}
          </a>

          {!outputs.length && (
            <p className="muted">
              No processed outputs are listed yet. The player will work once
              the selected profile is available.
            </p>
          )}
        </div>
      )}

      {tab === 'thumbnails' && (
        <div className="panel">
          <h3>Generated thumbnails</h3>
          <p className="muted">
            Preview thumbnail profiles generated by the Thumbnail Service.
          </p>

          <div className="thumb-grid">
            {(
              Array.isArray(thumbs)
                ? thumbs
                : (thumbs as { items?: unknown[] } | null)?.items || []
            ).map((thumbnail, index) => {
              const item =
                typeof thumbnail === 'string'
                  ? thumbnail
                  : String(
                      (thumbnail as { profile?: string })?.profile ||
                        'thumbnail',
                    );

              return (
                <div className="thumb-card" key={index}>
                  <img
                    src={videoApi.thumbnailUrl(id, item)}
                    onError={(e) => {
                      (e.currentTarget as HTMLImageElement).style.display =
                        'none';
                    }}
                  />
                  <b>{item}</b>
                </div>
              );
            })}
          </div>

          {!thumbs && (
            <p className="muted">
              Thumbnail information is not available yet.
            </p>
          )}
        </div>
      )}
    </section>
  );
}

function Info({
  label,
  value,
}: {
  label: string;
  value?: string | number;
}) {
  return (
    <div className="info-row">
      <span>{label}</span>
      <b>{value ?? '—'}</b>
    </div>
  );
}

function Loading() {
  return (
    <div className="loading">
      <span className="spinner" />
      Loading your workspace…
    </div>
  );
}

function Empty({ title, text }: { title: string; text: string }) {
  return (
    <div className="empty-state">
      <h3>{title}</h3>
      <p className="muted">{text}</p>
    </div>
  );
}

export default App;
