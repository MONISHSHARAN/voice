import React from 'react';
import { Link } from 'react-router-dom';
import { Phone, Clock, Shield, Heart, ArrowRight, CheckCircle } from 'lucide-react';

const Home = () => {
  const features = [
    {
      icon: <Phone className="h-8 w-8 text-green-600" />,
      title: "AI-Powered Calls",
      description: "Our intelligent AI assistant calls you to discuss your symptoms and schedule appointments."
    },
    {
      icon: <Clock className="h-8 w-8 text-blue-600" />,
      title: "Instant Scheduling",
      description: "Get appointments scheduled automatically based on your condition and location."
    },
    {
      icon: <Shield className="h-8 w-8 text-purple-600" />,
      title: "Secure & Private",
      description: "Your health information is protected with enterprise-grade security measures."
    },
    {
      icon: <Heart className="h-8 w-8 text-red-600" />,
      title: "Expert Care",
      description: "Connect with specialized healthcare professionals for your specific medical needs."
    }
  ];

  const steps = [
    {
      number: "1",
      title: "Submit Your Information",
      description: "Fill out a simple form with your symptoms and contact details."
    },
    {
      number: "2",
      title: "AI Assistant Calls You",
      description: "Our AI will call you to discuss your symptoms and ask relevant questions."
    },
    {
      number: "3",
      title: "Get Your Appointment",
      description: "We'll schedule you with the best specialist and send confirmation details."
    }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Welcome to MedAgg Healthcare
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-green-100">
              AI-powered healthcare that calls you back. Get the care you need, when you need it.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/book-appointment"
                className="bg-white text-green-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors duration-200 flex items-center justify-center"
              >
                Book Appointment Now
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <button className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold text-lg hover:bg-white hover:text-green-600 transition-colors duration-200">
                Learn More
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Why Choose MedAgg?
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Experience healthcare like never before with our innovative AI-powered system
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="text-center p-6 rounded-lg hover:shadow-lg transition-shadow duration-200">
                <div className="flex justify-center mb-4">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get started in just three simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="text-center">
                <div className="flex justify-center mb-6">
                  <div className="bg-green-600 text-white rounded-full w-16 h-16 flex items-center justify-center text-2xl font-bold">
                    {step.number}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-4">
                  {step.title}
                </h3>
                <p className="text-gray-600">
                  {step.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Specializations Section */}
      <div className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Specializations
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Expert care for interventional cardiology conditions
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-8 rounded-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                Chronic Total Occlusion
              </h3>
              <p className="text-gray-600 mb-4">
                Specialized treatment for completely blocked coronary arteries using advanced techniques.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Minimally invasive procedures
                </li>
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Expert interventional cardiologists
                </li>
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Advanced imaging technology
                </li>
              </ul>
            </div>
            
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-8 rounded-lg">
              <h3 className="text-2xl font-semibold text-gray-900 mb-4">
                Radiofrequency Ablation
              </h3>
              <p className="text-gray-600 mb-4">
                Precise treatment for heart rhythm disorders using radiofrequency energy.
              </p>
              <ul className="space-y-2">
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  High success rates
                </li>
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Minimally invasive approach
                </li>
                <li className="flex items-center text-gray-700">
                  <CheckCircle className="h-5 w-5 text-green-600 mr-2" />
                  Quick recovery time
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-green-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            Ready to Get Started?
          </h2>
          <p className="text-xl text-green-100 mb-8">
            Book your appointment today and experience the future of healthcare
          </p>
          <Link
            to="/book-appointment"
            className="bg-white text-green-600 px-8 py-4 rounded-lg font-semibold text-lg hover:bg-gray-100 transition-colors duration-200 inline-flex items-center"
          >
            Book Your Appointment
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;


