import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { Phone, User, Calendar, MapPin, FileText, Heart } from 'lucide-react';
import axios from 'axios';

const PatientForm = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();
  
  const { register, handleSubmit, formState: { errors }, watch } = useForm();
  const selectedCategory = watch('medical_category');

  const submitForm = async (data) => {
    try {
      const response = await axios.post('http://localhost:8000/api/patients', data);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to submit form');
    }
  };

  const mutation = useMutation(submitForm, {
    onSuccess: (data) => {
      toast.success('Form submitted successfully! Our AI assistant will call you shortly.');
      navigate(`/call-status/${data.id}`);
    },
    onError: (error) => {
      toast.error(error.message);
    },
    onSettled: () => {
      setIsSubmitting(false);
    }
  });

  const onSubmit = (data) => {
    setIsSubmitting(true);
    mutation.mutate(data);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="text-center mb-8">
            <div className="flex justify-center mb-4">
              <div className="bg-green-100 p-3 rounded-full">
                <Heart className="h-8 w-8 text-green-600" />
              </div>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Book Your Appointment
            </h1>
            <p className="text-gray-600">
              Fill out the form below and our AI assistant will call you to schedule your appointment
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Personal Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <User className="h-5 w-5 mr-2 text-green-600" />
                Personal Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    {...register('name', { required: 'Name is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Enter your full name"
                  />
                  {errors.name && (
                    <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Age *
                  </label>
                  <input
                    type="number"
                    {...register('age', { 
                      required: 'Age is required',
                      min: { value: 0, message: 'Age must be positive' },
                      max: { value: 120, message: 'Age must be less than 120' }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="Enter your age"
                  />
                  {errors.age && (
                    <p className="text-red-500 text-sm mt-1">{errors.age.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Gender *
                  </label>
                  <select
                    {...register('gender', { required: 'Gender is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </select>
                  {errors.gender && (
                    <p className="text-red-500 text-sm mt-1">{errors.gender.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Phone Number *
                  </label>
                  <input
                    type="tel"
                    {...register('phone_number', { 
                      required: 'Phone number is required',
                      pattern: {
                        value: /^\+?1?\d{9,15}$/,
                        message: 'Please enter a valid phone number'
                      }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="+1 (555) 123-4567"
                  />
                  {errors.phone_number && (
                    <p className="text-red-500 text-sm mt-1">{errors.phone_number.message}</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Language Preference *
                  </label>
                  <select
                    {...register('language_preference', { required: 'Language preference is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">Select language</option>
                    <option value="english">English</option>
                    <option value="tamil">தமிழ் (Tamil)</option>
                    <option value="hindi">हिन्दी (Hindi)</option>
                  </select>
                  {errors.language_preference && (
                    <p className="text-red-500 text-sm mt-1">{errors.language_preference.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location *
                  </label>
                  <input
                    type="text"
                    {...register('location', { required: 'Location is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    placeholder="City, State (e.g., New York, NY)"
                  />
                  {errors.location && (
                    <p className="text-red-500 text-sm mt-1">{errors.location.message}</p>
                  )}
                </div>
              </div>
            </div>

            {/* Medical Information */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Heart className="h-5 w-5 mr-2 text-green-600" />
                Medical Information
              </h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Medical Category *
                </label>
                <select
                  {...register('medical_category', { required: 'Medical category is required' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  <option value="">Select medical category</option>
                  <option value="interventional_cardiology">Interventional Cardiology</option>
                </select>
                {errors.medical_category && (
                  <p className="text-red-500 text-sm mt-1">{errors.medical_category.message}</p>
                )}
              </div>

              {selectedCategory === 'interventional_cardiology' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Sub-Category *
                  </label>
                  <select
                    {...register('sub_category', { required: 'Sub-category is required' })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  >
                    <option value="">Select sub-category</option>
                    <option value="chronic_total_occlusion">Chronic Total Occlusion</option>
                    <option value="radiofrequency_ablation">Radiofrequency Ablation</option>
                  </select>
                  {errors.sub_category && (
                    <p className="text-red-500 text-sm mt-1">{errors.sub_category.message}</p>
                  )}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Problem Description *
                </label>
                <textarea
                  {...register('problem_description', { 
                    required: 'Problem description is required',
                    minLength: { value: 10, message: 'Please provide more details (at least 10 characters)' }
                  })}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  placeholder="Please describe your symptoms and medical concerns in detail..."
                />
                {errors.problem_description && (
                  <p className="text-red-500 text-sm mt-1">{errors.problem_description.message}</p>
                )}
              </div>
            </div>

            {/* Submit Button */}
            <div className="pt-6">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full bg-green-600 text-white py-3 px-6 rounded-md font-semibold text-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center"
              >
                {isSubmitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Phone className="h-5 w-5 mr-2" />
                    Submit & Get AI Call
                  </>
                )}
              </button>
            </div>
          </form>

          {/* Information Box */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">What happens next?</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Our AI assistant will call you within 5 minutes</li>
              <li>• We'll discuss your symptoms and ask relevant questions</li>
              <li>• We'll schedule you with the best specialist in your area</li>
              <li>• You'll receive a confirmation email with all details</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientForm;
