import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from 'react-query';
import { Phone, PhoneCall, PhoneOff, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import axios from 'axios';

const CallStatus = () => {
  const { callId } = useParams();
  const [callStatus, setCallStatus] = useState('initiated');
  const [conversationLog, setConversationLog] = useState([]);

  // Fetch call session details
  const { data: callSession, isLoading, refetch } = useQuery(
    ['callSession', callId],
    () => axios.get(`http://localhost:8000/api/calls/${callId}`).then(res => res.data),
    {
      refetchInterval: 2000, // Poll every 2 seconds
      enabled: !!callId
    }
  );

  useEffect(() => {
    if (callSession) {
      setCallStatus(callSession.status);
      setConversationLog(callSession.conversation_log || []);
    }
  }, [callSession]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'initiated':
        return <Clock className="h-6 w-6 text-blue-500" />;
      case 'ringing':
        return <PhoneCall className="h-6 w-6 text-yellow-500 animate-pulse" />;
      case 'in_progress':
        return <Phone className="h-6 w-6 text-green-500" />;
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-600" />;
      case 'failed':
      case 'no_answer':
        return <PhoneOff className="h-6 w-6 text-red-500" />;
      default:
        return <AlertCircle className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusMessage = (status) => {
    switch (status) {
      case 'initiated':
        return 'Preparing to call you...';
      case 'ringing':
        return 'Calling you now...';
      case 'in_progress':
        return 'Speaking with our AI assistant...';
      case 'completed':
        return 'Call completed successfully!';
      case 'failed':
        return 'Call failed. Please try again.';
      case 'no_answer':
        return 'No answer. We will try again shortly.';
      default:
        return 'Unknown status';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'initiated':
        return 'bg-blue-100 text-blue-800';
      case 'ringing':
        return 'bg-yellow-100 text-yellow-800';
      case 'in_progress':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
      case 'no_answer':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading call status...</p>
        </div>
      </div>
    );
  }

  if (!callSession) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Call Not Found</h2>
          <p className="text-gray-600">The call session you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Call Status</h1>
          <p className="text-gray-600">Track your AI assistant call in real-time</p>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="text-center">
            <div className="flex justify-center mb-4">
              {getStatusIcon(callStatus)}
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {getStatusMessage(callStatus)}
            </h2>
            <div className="inline-flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-800 mb-4">
              Status: <span className={`ml-2 px-2 py-1 rounded-full text-xs ${getStatusColor(callStatus)}`}>
                {callStatus.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            <p className="text-gray-600">
              Call Session ID: <span className="font-mono text-sm">{callId}</span>
            </p>
          </div>
        </div>

        {/* Conversation Log */}
        {conversationLog.length > 0 && (
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-6">Conversation Log</h3>
            <div className="space-y-4">
              {conversationLog.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.role === 'user'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-200 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                    <p className="text-xs opacity-75 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Next Steps */}
        {callStatus === 'completed' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mt-8">
            <div className="flex items-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-600 mr-2" />
              <h3 className="text-lg font-semibold text-green-900">Call Completed Successfully!</h3>
            </div>
            <div className="text-green-800">
              <p className="mb-2">Your appointment has been scheduled and you should receive a confirmation email shortly.</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Check your email for appointment details</li>
                <li>Arrive 15 minutes early for your appointment</li>
                <li>Bring a list of your current medications</li>
                <li>Bring any previous test results</li>
              </ul>
            </div>
          </div>
        )}

        {/* Error State */}
        {(callStatus === 'failed' || callStatus === 'no_answer') && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 mt-8">
            <div className="flex items-center mb-4">
              <AlertCircle className="h-6 w-6 text-red-600 mr-2" />
              <h3 className="text-lg font-semibold text-red-900">Call Issue</h3>
            </div>
            <div className="text-red-800">
              <p className="mb-2">
                {callStatus === 'failed' 
                  ? 'There was an issue with the call. Please try submitting your form again.'
                  : 'We couldn\'t reach you. We will try calling again shortly.'
                }
              </p>
              <button
                onClick={() => window.location.href = '/book-appointment'}
                className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors duration-200"
              >
                Try Again
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {(callStatus === 'initiated' || callStatus === 'ringing' || callStatus === 'in_progress') && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
            <div className="flex items-center mb-4">
              <Clock className="h-6 w-6 text-blue-600 mr-2" />
              <h3 className="text-lg font-semibold text-blue-900">Call in Progress</h3>
            </div>
            <div className="text-blue-800">
              <p className="mb-2">Please wait while we connect you with our AI assistant.</p>
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                <span className="text-sm">This page will update automatically...</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CallStatus;


