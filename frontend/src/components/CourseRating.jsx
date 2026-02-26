import { useState } from 'react';
import { Star } from 'lucide-react';
import api from '../utils/api';
import toast from 'react-hot-toast';

const CourseRating = ({ courseId, initialRating = 0, userRating = 0, totalRatings = 0, onRatingUpdate }) => {
  const [hoveredRating, setHoveredRating] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleRating = async (rating) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      const response = await api.post(`/courses/${courseId}/rate`, {
        rating: rating
      });
      
      if (response.data.success) {
        toast.success('Rating submitted successfully!');
        if (onRatingUpdate) {
          onRatingUpdate(response.data.average_rating, response.data.total_ratings);
        }
      }
    } catch (error) {
      console.error('Failed to submit rating:', error);
      if (error.response?.status === 401) {
        toast.error('Please login to rate this course');
      } else if (error.response?.data?.message) {
        toast.error(error.response.data.message);
      } else {
        toast.error('Failed to submit rating');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStars = (interactive = false) => {
    const stars = [];
    const displayRating = hoveredRating || (interactive ? userRating : initialRating);
    
    for (let i = 1; i <= 5; i++) {
      stars.push(
        <button
          key={i}
          type="button"
          disabled={!interactive || isSubmitting}
          onClick={() => interactive && handleRating(i)}
          onMouseEnter={() => interactive && setHoveredRating(i)}
          onMouseLeave={() => interactive && setHoveredRating(0)}
          className={`${interactive ? 'cursor-pointer hover:scale-110' : 'cursor-default'} transition-transform ${
            isSubmitting ? 'opacity-50' : ''
          }`}
        >
          <Star
            className={`w-5 h-5 ${
              i <= displayRating
                ? 'fill-yellow-400 text-yellow-400'
                : 'fill-none text-gray-300'
            }`}
          />
        </button>
      );
    }
    return stars;
  };

  return (
    <div className="flex items-center space-x-2">
      <div className="flex items-center space-x-1">
        {renderStars(true)}
      </div>
      <div className="text-sm text-gray-600">
        <span className="font-medium">{initialRating.toFixed(1)}</span>
        {totalRatings > 0 && (
          <span className="text-gray-400"> ({totalRatings})</span>
        )}
      </div>
    </div>
  );
};

export default CourseRating;
