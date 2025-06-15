import React, { useState, useEffect } from 'react';
import { Layout } from '../layout/Layout';
import { Clock, Star, Camera, Play, RotateCcw } from 'lucide-react';
import { Button } from '../ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { cookingServiceGetUserCookingSessions, cookingServiceStartCookingSession } from '../../lib/sdk';
import type { CookingSession } from '../../lib/sdk';
import { useNavigate } from 'react-router-dom';

export function SessionsPage() {
  const [sessions, setSessions] = useState<CookingSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'completed' | 'in_progress'>('all');
  const navigate = useNavigate();

  // Temporary user ID - in real app this would come from auth
  const userId = "demo-user-1";

  useEffect(() => {
    loadCookingSessions();
  }, []);

  const loadCookingSessions = async () => {
    try {
      setIsLoading(true);
      const response = await cookingServiceGetUserCookingSessions({
        body: { user_id: userId }
      });
      if (response.data) {
        setSessions(response.data);
      }
    } catch (error) {
      console.error('Failed to load cooking sessions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleContinueSession = (sessionId: string) => {
    navigate(`/cooking/${sessionId}`);
  };

  const handleReplaySession = async (sessionId: string) => {
    // In a real app, you'd create a new session based on the original recipe
    navigate(`/cooking/${sessionId}`);
  };

  const filteredSessions = sessions.filter(session => {
    if (filter === 'all') return true;
    return session.status === filter;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'abandoned': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateProgress = (session: CookingSession) => {
    const totalSteps = session.final_steps?.length || 1;
    return Math.round((session.current_step / totalSteps) * 100);
  };

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-3xl font-bold text-gray-900">My Cooking Quests</h1>
          <p className="text-gray-600">Track your culinary adventures and replay favorite recipes</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatsCard
            title="Total Quests"
            value={sessions.length.toString()}
            icon={<Play className="h-5 w-5" />}
          />
          <StatsCard
            title="Completed"
            value={sessions.filter(s => s.status === 'completed').length.toString()}
            icon={<Star className="h-5 w-5" />}
          />
          <StatsCard
            title="In Progress"
            value={sessions.filter(s => s.status === 'in_progress').length.toString()}
            icon={<Clock className="h-5 w-5" />}
          />
          <StatsCard
            title="Photos Taken"
            value={sessions.reduce((total, s) => total + (s.session_photos?.length || 0), 0).toString()}
            icon={<Camera className="h-5 w-5" />}
          />
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          <Button
            variant={filter === 'all' ? 'default' : 'outline'}
            onClick={() => setFilter('all')}
          >
            All Sessions
          </Button>
          <Button
            variant={filter === 'completed' ? 'default' : 'outline'}
            onClick={() => setFilter('completed')}
          >
            Completed
          </Button>
          <Button
            variant={filter === 'in_progress' ? 'default' : 'outline'}
            onClick={() => setFilter('in_progress')}
          >
            In Progress
          </Button>
        </div>

        {/* Sessions */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto"></div>
            <p className="text-gray-600 mt-2">Loading cooking sessions...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <EmptyState filter={filter} />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSessions.map((session) => (
              <SessionCard
                key={session.id}
                session={session}
                onContinue={() => session.id && handleContinueSession(session.id)}
                onReplay={() => session.id && handleReplaySession(session.id)}
              />
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}

interface StatsCardProps {
  title: string;
  value: string;
  icon: React.ReactNode;
}

function StatsCard({ title, value, icon }: StatsCardProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center space-x-3">
          <div className="text-orange-600">{icon}</div>
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

interface SessionCardProps {
  session: CookingSession;
  onContinue: () => void;
  onReplay: () => void;
}

function SessionCard({ session, onContinue, onReplay }: SessionCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'abandoned': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const calculateProgress = (session: CookingSession) => {
    const totalSteps = session.final_steps?.length || 1;
    return Math.round((session.current_step / totalSteps) * 100);
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start mb-2">
          <CardTitle className="text-lg">Cooking Quest</CardTitle>
          <Badge className={getStatusColor(session.status)}>
            {session.status.replace('_', ' ')}
          </Badge>
        </div>
        <p className="text-sm text-gray-600">
          Started {formatDate(session.started_at)}
        </p>
      </CardHeader>
      
      <CardContent className="space-y-4">
        {/* Progress */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span>Progress</span>
            <span>{calculateProgress(session)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-orange-600 h-2 rounded-full" 
              style={{ width: `${calculateProgress(session)}%` }}
            ></div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-600">Decisions</p>
            <p className="font-medium">{session.decisions_made?.length || 0}</p>
          </div>
          <div>
            <p className="text-gray-600">Photos</p>
            <p className="font-medium">{session.session_photos?.length || 0}</p>
          </div>
          <div>
            <p className="text-gray-600">Time</p>
            <p className="font-medium">{session.total_time_minutes}m</p>
          </div>
          <div>
            <p className="text-gray-600">Rating</p>
            <div className="flex items-center">
              {session.rating ? (
                <>
                  <Star className="h-3 w-3 text-yellow-400 fill-current mr-1" />
                  <span className="font-medium">{session.rating}</span>
                </>
              ) : (
                <span className="text-gray-400">-</span>
              )}
            </div>
          </div>
        </div>

        {/* Nutrition highlight */}
        {session.final_nutrition && (
          <div className="bg-orange-50 p-3 rounded-md">
            <p className="text-sm font-medium text-orange-800 mb-1">Final dish:</p>
            <p className="text-xs text-orange-700">
              {Math.round(session.final_nutrition.calories || 0)} cal, 
              {Math.round(session.final_nutrition.protein || 0)}g protein
            </p>
          </div>
        )}

        {/* Photos preview */}
        {session.session_photos && session.session_photos.length > 0 && (
          <div className="flex gap-2 overflow-x-auto">
            {session.session_photos.slice(0, 3).map((photo, index) => (
              <img
                key={index}
                src={photo}
                alt={`Session photo ${index + 1}`}
                className="w-16 h-16 object-cover rounded-md flex-shrink-0"
              />
            ))}
            {session.session_photos.length > 3 && (
              <div className="w-16 h-16 bg-gray-100 rounded-md flex items-center justify-center text-xs text-gray-600">
                +{session.session_photos.length - 3}
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          {session.status === 'in_progress' ? (
            <Button
              onClick={onContinue}
              className="flex-1 bg-orange-600 hover:bg-orange-700"
            >
              <Play className="h-4 w-4 mr-2" />
              Continue
            </Button>
          ) : (
            <Button
              onClick={onReplay}
              variant="outline"
              className="flex-1"
            >
              <RotateCcw className="h-4 w-4 mr-2" />
              Replay
            </Button>
          )}
        </div>

        {/* Notes */}
        {session.notes && (
          <div className="pt-2 border-t">
            <p className="text-xs text-gray-600 italic">
              "{session.notes}"
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface EmptyStateProps {
  filter: string;
}

function EmptyState({ filter }: EmptyStateProps) {
  const getMessage = () => {
    switch (filter) {
      case 'completed': return 'No completed cooking quests yet';
      case 'in_progress': return 'No cooking quests in progress';
      default: return 'No cooking quests yet';
    }
  };

  return (
    <div className="text-center py-12">
      <Clock className="h-16 w-16 text-gray-400 mx-auto mb-4" />
      <h3 className="text-xl font-semibold text-gray-900 mb-2">{getMessage()}</h3>
      <p className="text-gray-600 mb-6">
        Start your first cooking adventure by exploring recipes
      </p>
      <Button className="bg-orange-600 hover:bg-orange-700">
        <Play className="h-4 w-4 mr-2" />
        Start a Quest
      </Button>
    </div>
  );
}