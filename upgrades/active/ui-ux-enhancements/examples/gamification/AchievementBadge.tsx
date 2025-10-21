/**
 * AchievementBadge.tsx
 *
 * Gamification achievement badge component with unlock animations.
 * Displays user achievements with visual appeal.
 *
 * Features:
 * - Achievement unlock animation
 * - Badge icons and colors
 * - Progress towards achievement
 * - Toast notifications for new achievements
 * - Achievement gallery view
 *
 * Usage:
 * ```tsx
 * // Single badge display
 * <AchievementBadge achievement={achievement} />
 *
 * // Unlock notification
 * <AchievementUnlockToast achievement={newAchievement} />
 * ```
 *
 * API Integration:
 * - GET /api/v1/gamification/achievements
 * - POST /api/v1/gamification/achievements/claim
 *
 * @see PLANNING.md Phase 3 for implementation details
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Award,
  TrendingUp,
  Search,
  MessageCircle,
  Users,
  Flame,
  Trophy,
  Star,
  Target,
  Zap
} from 'lucide-react';

export interface Achievement {
  uuid: string;
  type: string; // 'knowledge_explorer' | 'deep_diver' | 'pattern_detective' | etc.
  title: string;
  description: string;
  icon: string; // Icon name
  tier: 'bronze' | 'silver' | 'gold' | 'platinum';
  progress?: number; // 0-100
  unlocked: boolean;
  unlocked_at?: string;
  metadata?: Record<string, any>;
}

interface AchievementBadgeProps {
  achievement: Achievement;
  size?: 'sm' | 'md' | 'lg';
  showProgress?: boolean;
  onClick?: () => void;
}

// Icon mapping
const iconMap: Record<string, React.ReactNode> = {
  search: <Search />,
  award: <Award />,
  trending: <TrendingUp />,
  message: <MessageCircle />,
  users: <Users />,
  flame: <Flame />,
  trophy: <Trophy />,
  star: <Star />,
  target: <Target />,
  zap: <Zap />
};

// Tier colors
const tierColors = {
  bronze: {
    bg: 'from-orange-900/20 to-amber-900/20',
    border: 'border-orange-500/30',
    text: 'text-orange-400',
    glow: 'shadow-orange-500/20'
  },
  silver: {
    bg: 'from-gray-700/20 to-gray-600/20',
    border: 'border-gray-400/30',
    text: 'text-gray-300',
    glow: 'shadow-gray-400/20'
  },
  gold: {
    bg: 'from-yellow-900/20 to-amber-700/20',
    border: 'border-yellow-500/30',
    text: 'text-yellow-400',
    glow: 'shadow-yellow-500/20'
  },
  platinum: {
    bg: 'from-purple-900/20 to-pink-900/20',
    border: 'border-purple-500/30',
    text: 'text-purple-400',
    glow: 'shadow-purple-500/20'
  }
};

// Size mappings
const sizeMap = {
  sm: {
    container: 'w-20 h-20',
    icon: 20,
    text: 'text-xs'
  },
  md: {
    container: 'w-32 h-32',
    icon: 32,
    text: 'text-sm'
  },
  lg: {
    container: 'w-48 h-48',
    icon: 48,
    text: 'text-base'
  }
};

export function AchievementBadge({
  achievement,
  size = 'md',
  showProgress = true,
  onClick
}: AchievementBadgeProps) {
  const colors = tierColors[achievement.tier];
  const sizing = sizeMap[size];
  const icon = iconMap[achievement.icon] || <Award />;

  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={onClick}
      className={`relative ${onClick ? 'cursor-pointer' : ''}`}
    >
      <div
        className={`${sizing.container} rounded-2xl bg-gradient-to-br ${colors.bg}
                   border-2 ${colors.border} ${colors.glow} shadow-lg
                   flex flex-col items-center justify-center gap-2
                   ${!achievement.unlocked ? 'grayscale opacity-40' : ''}
                   transition-all duration-300`}
      >
        {/* Icon */}
        <div className={colors.text}>
          {React.cloneElement(icon as React.ReactElement, {
            size: sizing.icon
          })}
        </div>

        {/* Tier badge */}
        <div className={`${colors.text} ${sizing.text} font-semibold uppercase tracking-wider`}>
          {achievement.tier}
        </div>

        {/* Lock overlay for locked achievements */}
        {!achievement.unlocked && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-white/20">
              🔒
            </div>
          </div>
        )}

        {/* Progress ring (for unlocked achievements with progress) */}
        {achievement.unlocked && showProgress && achievement.progress !== undefined && (
          <svg className="absolute inset-0 w-full h-full -rotate-90">
            <circle
              cx="50%"
              cy="50%"
              r="45%"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              className="text-white/10"
            />
            <circle
              cx="50%"
              cy="50%"
              r="45%"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeDasharray={`${achievement.progress * 2.83} 283`}
              className={colors.text}
            />
          </svg>
        )}
      </div>

      {/* Title (below badge for large size) */}
      {size === 'lg' && (
        <div className="mt-3 text-center">
          <h3 className="font-semibold text-white">{achievement.title}</h3>
          <p className="text-sm text-white/60 mt-1">{achievement.description}</p>
          {achievement.unlocked && achievement.unlocked_at && (
            <p className="text-xs text-white/40 mt-2">
              Unlocked {new Date(achievement.unlocked_at).toLocaleDateString()}
            </p>
          )}
        </div>
      )}
    </motion.div>
  );
}

/**
 * AchievementUnlockToast
 *
 * Toast notification shown when user unlocks a new achievement.
 * Auto-dismisses after 5 seconds.
 */
interface AchievementUnlockToastProps {
  achievement: Achievement;
  onDismiss: () => void;
}

export function AchievementUnlockToast({ achievement, onDismiss }: AchievementUnlockToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(onDismiss, 300); // Wait for exit animation
    }, 5000);

    return () => clearTimeout(timer);
  }, [onDismiss]);

  const colors = tierColors[achievement.tier];

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          className="fixed bottom-6 right-6 z-50"
        >
          <div className={`backdrop-blur-xl bg-gradient-to-br ${colors.bg}
                         border-2 ${colors.border} ${colors.glow} shadow-2xl
                         rounded-2xl p-6 min-w-[320px] max-w-md`}>
            <div className="flex items-start gap-4">
              {/* Trophy icon */}
              <div className={`${colors.text} flex-shrink-0`}>
                <Trophy size={32} />
              </div>

              {/* Content */}
              <div className="flex-1">
                <h3 className="font-bold text-lg text-white mb-1">
                  Achievement Unlocked! 🎉
                </h3>
                <p className={`${colors.text} font-semibold mb-1`}>
                  {achievement.title}
                </p>
                <p className="text-white/60 text-sm">
                  {achievement.description}
                </p>
              </div>

              {/* Close button */}
              <button
                onClick={() => {
                  setIsVisible(false);
                  setTimeout(onDismiss, 300);
                }}
                className="text-white/40 hover:text-white/80 transition flex-shrink-0"
              >
                ✕
              </button>
            </div>

            {/* Progress bar animation */}
            <motion.div
              initial={{ scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 5 }}
              className={`mt-4 h-1 bg-gradient-to-r ${colors.bg} rounded-full origin-left`}
            />
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * AchievementsPanel
 *
 * Full achievement gallery showing all achievements (locked and unlocked).
 */
interface AchievementsPanelProps {
  achievements: Achievement[];
  onAchievementClick?: (achievement: Achievement) => void;
}

export function AchievementsPanel({ achievements, onAchievementClick }: AchievementsPanelProps) {
  const [filter, setFilter] = useState<'all' | 'unlocked' | 'locked'>('all');

  // Calculate stats
  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalCount = achievements.length;
  const completionPercentage = Math.round((unlockedCount / totalCount) * 100);

  // Filter achievements
  const filteredAchievements = achievements.filter(a => {
    if (filter === 'all') return true;
    if (filter === 'unlocked') return a.unlocked;
    if (filter === 'locked') return !a.unlocked;
    return true;
  });

  // Group by tier
  const groupedAchievements = filteredAchievements.reduce((acc, achievement) => {
    if (!acc[achievement.tier]) acc[achievement.tier] = [];
    acc[achievement.tier].push(achievement);
    return acc;
  }, {} as Record<string, Achievement[]>);

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Achievements</h2>
        <p className="text-white/60">
          Track your knowledge exploration progress
        </p>

        {/* Stats */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{unlockedCount}</div>
            <div className="text-sm text-white/60">Unlocked</div>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{totalCount}</div>
            <div className="text-sm text-white/60">Total</div>
          </div>
          <div className="bg-white/5 border border-white/10 rounded-lg p-4">
            <div className="text-2xl font-bold text-white">{completionPercentage}%</div>
            <div className="text-sm text-white/60">Complete</div>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-4 h-2 bg-white/5 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${completionPercentage}%` }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
          />
        </div>
      </div>

      {/* Filter buttons */}
      <div className="flex gap-2 mb-6">
        {(['all', 'unlocked', 'locked'] as const).map(filterOption => (
          <button
            key={filterOption}
            onClick={() => setFilter(filterOption)}
            className={`px-4 py-2 rounded-lg font-medium transition capitalize
                     ${filter === filterOption
                       ? 'bg-purple-500 text-white'
                       : 'bg-white/5 text-white/60 hover:bg-white/10'
                     }`}
          >
            {filterOption}
          </button>
        ))}
      </div>

      {/* Achievement grid by tier */}
      <div className="space-y-8">
        {(['platinum', 'gold', 'silver', 'bronze'] as const).map(tier => {
          const tierAchievements = groupedAchievements[tier] || [];
          if (tierAchievements.length === 0) return null;

          return (
            <div key={tier}>
              <h3 className={`text-xl font-semibold mb-4 capitalize ${tierColors[tier].text}`}>
                {tier} Achievements
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {tierAchievements.map(achievement => (
                  <div key={achievement.uuid}>
                    <AchievementBadge
                      achievement={achievement}
                      size="md"
                      onClick={() => onAchievementClick?.(achievement)}
                    />
                    <div className="mt-2 text-center">
                      <p className="font-medium text-sm text-white">
                        {achievement.title}
                      </p>
                      {achievement.progress !== undefined && !achievement.unlocked && (
                        <p className="text-xs text-white/40 mt-1">
                          {achievement.progress}% complete
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/**
 * StreakCounter
 *
 * Display user's current and longest streak.
 */
interface StreakCounterProps {
  currentStreak: number;
  longestStreak: number;
  lastActivityDate: string;
}

export function StreakCounter({ currentStreak, longestStreak, lastActivityDate }: StreakCounterProps) {
  const lastActivity = new Date(lastActivityDate);
  const today = new Date();
  const daysSinceActivity = Math.floor((today.getTime() - lastActivity.getTime()) / (1000 * 60 * 60 * 24));

  const isStreakActive = daysSinceActivity <= 1;

  return (
    <div className="bg-gradient-to-br from-orange-900/20 to-red-900/20 border-2 border-orange-500/30 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Activity Streak</h3>
        <Flame className={`${isStreakActive ? 'text-orange-400' : 'text-white/20'}`} size={24} />
      </div>

      {/* Current streak */}
      <div className="text-center mb-4">
        <motion.div
          key={currentStreak}
          initial={{ scale: 1.2, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-5xl font-bold text-orange-400 mb-2"
        >
          {currentStreak}
        </motion.div>
        <p className="text-white/60">
          {currentStreak === 1 ? 'day' : 'days'} streak
        </p>
      </div>

      {/* Longest streak */}
      <div className="flex items-center justify-between pt-4 border-t border-white/10">
        <span className="text-sm text-white/60">Longest streak:</span>
        <span className="text-sm font-semibold text-white">{longestStreak} days</span>
      </div>

      {/* Motivation message */}
      {!isStreakActive && (
        <div className="mt-4 p-3 bg-white/5 rounded-lg text-sm text-white/60">
          Your streak ended. Come back daily to build your streak! 🔥
        </div>
      )}
    </div>
  );
}
