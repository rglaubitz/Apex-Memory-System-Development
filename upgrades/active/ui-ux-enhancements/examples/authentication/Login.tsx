/**
 * Login.tsx
 *
 * User authentication login form component.
 * Handles user login with JWT token management.
 *
 * Features:
 * - Email/password authentication
 * - Form validation with error messages
 * - Remember me functionality
 * - Password visibility toggle
 * - Loading states
 * - Redirect after successful login
 *
 * Usage:
 * ```tsx
 * <Login onSuccess={() => navigate('/dashboard')} />
 * ```
 *
 * API Integration:
 * - POST /api/v1/auth/login
 *
 * @see PLANNING.md Phase 1 for implementation details
 */

import React, { useState } from 'react';
import { Eye, EyeOff, Lock, Mail, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useAuth } from '@/lib/auth';
import { useNavigate } from 'react-router-dom';

interface LoginProps {
  onSuccess?: () => void;
  redirectTo?: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

export function Login({ onSuccess, redirectTo = '/dashboard' }: LoginProps) {
  const navigate = useNavigate();
  const { login } = useAuth();

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // UI state
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};

    // Email validation
    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = 'Invalid email address';
    }

    // Password validation
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle login
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous errors
    setErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      // Call login API
      await login(email, password, rememberMe);

      // Success callback
      if (onSuccess) {
        onSuccess();
      } else {
        navigate(redirectTo);
      }

    } catch (error: any) {
      // Handle different error types
      if (error.response?.status === 401) {
        setErrors({
          general: 'Invalid email or password. Please try again.'
        });
      } else if (error.response?.status === 429) {
        setErrors({
          general: 'Too many login attempts. Please try again later.'
        });
      } else {
        setErrors({
          general: 'An error occurred. Please try again later.'
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-4">
      {/* Neural background effect */}
      <div className="fixed inset-0 -z-10 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Card */}
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
              Welcome Back
            </h1>
            <p className="text-white/60">
              Sign in to access your knowledge base
            </p>
          </div>

          {/* General Error Message */}
          {errors.general && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg flex items-start gap-3"
            >
              <AlertCircle className="text-red-400 flex-shrink-0 mt-0.5" size={20} />
              <p className="text-red-400 text-sm">{errors.general}</p>
            </motion.div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2 text-white/80">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" size={20} />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className={`w-full pl-10 pr-4 py-3 bg-white/5 border rounded-lg
                           focus:outline-none focus:ring-2
                           ${errors.email
                             ? 'border-red-500/50 focus:ring-red-500/50'
                             : 'border-white/10 focus:ring-purple-500'
                           }
                           placeholder-white/30 transition`}
                  placeholder="you@company.com"
                  disabled={isLoading}
                  autoComplete="email"
                />
              </div>
              {errors.email && (
                <p className="mt-1.5 text-red-400 text-sm flex items-center gap-1">
                  <AlertCircle size={14} />
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2 text-white/80">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white/40" size={20} />
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className={`w-full pl-10 pr-12 py-3 bg-white/5 border rounded-lg
                           focus:outline-none focus:ring-2
                           ${errors.password
                             ? 'border-red-500/50 focus:ring-red-500/50'
                             : 'border-white/10 focus:ring-purple-500'
                           }
                           placeholder-white/30 transition`}
                  placeholder="••••••••"
                  disabled={isLoading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-white/40 hover:text-white/60 transition"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="mt-1.5 text-red-400 text-sm flex items-center gap-1">
                  <AlertCircle size={14} />
                  {errors.password}
                </p>
              )}
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-white/20 bg-white/5 text-purple-500
                           focus:ring-2 focus:ring-purple-500 focus:ring-offset-0
                           cursor-pointer"
                  disabled={isLoading}
                />
                <span className="text-sm text-white/60 group-hover:text-white/80 transition">
                  Remember me
                </span>
              </label>

              <a
                href="/forgot-password"
                className="text-sm text-purple-400 hover:text-purple-300 transition"
              >
                Forgot password?
              </a>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-gradient-to-r from-purple-500 to-pink-500
                       hover:from-purple-600 hover:to-pink-600
                       rounded-lg font-semibold transition
                       disabled:opacity-50 disabled:cursor-not-allowed
                       focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 focus:ring-offset-black"
            >
              {isLoading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-white/60">
              Don't have an account?{' '}
              <a
                href="/register"
                className="text-purple-400 hover:text-purple-300 transition font-medium"
              >
                Create one
              </a>
            </p>
          </div>

          {/* Divider */}
          <div className="mt-8 relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-black/50 text-white/40">
                Or continue with
              </span>
            </div>
          </div>

          {/* SSO Options (Optional) */}
          <div className="mt-6 grid grid-cols-2 gap-3">
            <button
              type="button"
              className="flex items-center justify-center gap-2 px-4 py-2.5
                       bg-white/5 hover:bg-white/10 border border-white/10
                       rounded-lg transition"
              disabled={isLoading}
            >
              {/* Google Icon */}
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="text-sm">Google</span>
            </button>

            <button
              type="button"
              className="flex items-center justify-center gap-2 px-4 py-2.5
                       bg-white/5 hover:bg-white/10 border border-white/10
                       rounded-lg transition"
              disabled={isLoading}
            >
              {/* Microsoft Icon */}
              <svg className="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#f25022" d="M0 0h11.5v11.5H0z" />
                <path fill="#00a4ef" d="M12.5 0H24v11.5H12.5z" />
                <path fill="#7fba00" d="M0 12.5h11.5V24H0z" />
                <path fill="#ffb900" d="M12.5 12.5H24V24H12.5z" />
              </svg>
              <span className="text-sm">Microsoft</span>
            </button>
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-white/40">
          By signing in, you agree to our{' '}
          <a href="/terms" className="text-white/60 hover:text-white/80 transition">
            Terms of Service
          </a>
          {' '}and{' '}
          <a href="/privacy" className="text-white/60 hover:text-white/80 transition">
            Privacy Policy
          </a>
        </p>
      </motion.div>
    </div>
  );
}
