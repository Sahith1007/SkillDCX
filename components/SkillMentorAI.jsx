'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { 
  Bot, 
  Send, 
  Sparkles, 
  BookOpen, 
  ExternalLink, 
  Star, 
  Clock,
  Target,
  Lightbulb,
  X
} from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const SkillMentorAI = () => {
  const [skills, setSkills] = useState([])
  const [currentSkill, setCurrentSkill] = useState('')
  const [focusAreas, setFocusAreas] = useState([])
  const [currentFocus, setCurrentFocus] = useState('')
  const [recommendations, setRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const { toast } = useToast()

  // Add skill to list
  const addSkill = () => {
    if (currentSkill.trim() && !skills.includes(currentSkill.trim().toLowerCase())) {
      setSkills([...skills, currentSkill.trim().toLowerCase()])
      setCurrentSkill('')
    }
  }

  // Remove skill from list
  const removeSkill = (skillToRemove) => {
    setSkills(skills.filter(skill => skill !== skillToRemove))
  }

  // Add focus area to list
  const addFocusArea = () => {
    if (currentFocus.trim() && !focusAreas.includes(currentFocus.trim().toLowerCase())) {
      setFocusAreas([...focusAreas, currentFocus.trim().toLowerCase()])
      setCurrentFocus('')
    }
  }

  // Remove focus area from list
  const removeFocusArea = (focusToRemove) => {
    setFocusAreas(focusAreas.filter(focus => focus !== focusToRemove))
  }

  // Get AI recommendations
  const getRecommendations = async () => {
    if (skills.length === 0) {
      toast({
        title: 'Skills Required',
        description: 'Please add at least one skill to get recommendations.',
        variant: 'destructive'
      })
      return
    }

    setIsLoading(true)
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/mentor`, {
        skills: skills,
        focus_areas: focusAreas
      })

      if (response.data.recommendations) {
        setRecommendations(response.data.recommendations)
        setHasSearched(true)
        
        toast({
          title: 'Recommendations Generated',
          description: `Found ${response.data.recommendations.length} personalized course recommendations!`,
        })
      } else {
        throw new Error('No recommendations received')
      }
    } catch (error) {
      console.error('Error getting recommendations:', error)
      toast({
        title: 'Recommendation Failed',
        description: error.response?.data?.detail || 'Failed to get AI recommendations',
        variant: 'destructive'
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Handle key press for skill input
  const handleSkillKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addSkill()
    }
  }

  // Handle key press for focus area input
  const handleFocusKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      addFocusArea()
    }
  }

  // Get provider badge color
  const getProviderColor = (provider) => {
    switch (provider.toLowerCase()) {
      case 'coursera':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'
      case 'udemy':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }
  }

  // Get level badge color
  const getLevelColor = (level) => {
    if (level.toLowerCase().includes('beginner')) {
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
    } else if (level.toLowerCase().includes('intermediate')) {
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
    } else if (level.toLowerCase().includes('advanced')) {
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }
    return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="border-dashed">
        <CardHeader className="text-center">
          <CardTitle className="flex items-center justify-center gap-2">
            <Bot className="h-6 w-6 text-primary" />
            AI Skill Mentor
            <Sparkles className="h-5 w-5 text-yellow-500" />
          </CardTitle>
          <CardDescription>
            Get personalized course recommendations based on your current skills and career goals
          </CardDescription>
        </CardHeader>
      </Card>

      {/* Skills Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Current Skills
          </CardTitle>
          <CardDescription>
            Add your existing skills (e.g., python, react, web3, machine learning)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter a skill..."
              value={currentSkill}
              onChange={(e) => setCurrentSkill(e.target.value)}
              onKeyPress={handleSkillKeyPress}
            />
            <Button onClick={addSkill} variant="outline">
              Add
            </Button>
          </div>
          
          {skills.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {skills.map((skill) => (
                <Badge 
                  key={skill} 
                  variant="secondary" 
                  className="flex items-center gap-1"
                >
                  {skill}
                  <X 
                    className="h-3 w-3 cursor-pointer hover:text-destructive" 
                    onClick={() => removeSkill(skill)}
                  />
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Focus Areas Input */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Lightbulb className="h-5 w-5" />
            Focus Areas (Optional)
          </CardTitle>
          <CardDescription>
            Specify areas you want to focus on (e.g., blockchain, data science, ai)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              placeholder="Enter focus area..."
              value={currentFocus}
              onChange={(e) => setCurrentFocus(e.target.value)}
              onKeyPress={handleFocusKeyPress}
            />
            <Button onClick={addFocusArea} variant="outline">
              Add
            </Button>
          </div>
          
          {focusAreas.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {focusAreas.map((focus) => (
                <Badge 
                  key={focus} 
                  variant="outline" 
                  className="flex items-center gap-1"
                >
                  {focus}
                  <X 
                    className="h-3 w-3 cursor-pointer hover:text-destructive" 
                    onClick={() => removeFocusArea(focus)}
                  />
                </Badge>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Get Recommendations Button */}
      <Card>
        <CardContent className="pt-6">
          <Button 
            onClick={getRecommendations} 
            disabled={isLoading || skills.length === 0}
            className="w-full"
            size="lg"
          >
            {isLoading ? (
              <>
                <Bot className="mr-2 h-4 w-4 animate-pulse" />
                Getting Recommendations...
              </>
            ) : (
              <>
                <Send className="mr-2 h-4 w-4" />
                Get AI Recommendations
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Recommendations */}
      {hasSearched && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Personalized Recommendations
              {recommendations.length > 0 && (
                <Badge variant="secondary">{recommendations.length} courses</Badge>
              )}
            </CardTitle>
            <CardDescription>
              AI-curated courses based on your skills and goals
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recommendations.length === 0 ? (
              <div className="text-center py-8">
                <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  No recommendations found. Try adding different skills or focus areas.
                </p>
              </div>
            ) : (
              <ScrollArea className="h-[600px] pr-4">
                <div className="space-y-4">
                  {recommendations.map((course, index) => (
                    <Card key={index} className="hover:shadow-md transition-shadow">
                      <CardContent className="pt-4">
                        <div className="flex justify-between items-start mb-3">
                          <div className="flex-1">
                            <h4 className="font-semibold text-lg mb-1">
                              {course.title}
                            </h4>
                            <p className="text-sm text-muted-foreground mb-2">
                              by {course.instructor}
                            </p>
                          </div>
                          <div className="flex flex-col gap-2">
                            <Badge 
                              className={getProviderColor(course.provider)}
                            >
                              {course.provider}
                            </Badge>
                            <Badge 
                              variant="outline" 
                              className={getLevelColor(course.level)}
                            >
                              {course.level}
                            </Badge>
                          </div>
                        </div>

                        <p className="text-sm text-muted-foreground mb-3">
                          {course.description}
                        </p>

                        <div className="flex items-center gap-4 mb-3">
                          <div className="flex items-center gap-1">
                            <Target className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              Skill: <Badge variant="outline">{course.skill_match}</Badge>
                            </span>
                          </div>
                          
                          {course.recommendation_type && (
                            <Badge 
                              variant={course.recommendation_type === 'skill_advancement' ? 'default' : 'secondary'}
                            >
                              {course.recommendation_type === 'skill_advancement' 
                                ? 'Level Up' 
                                : 'Next Skill'
                              }
                            </Badge>
                          )}

                          {course.focus_match && (
                            <Badge variant="default">
                              Focus Match
                            </Badge>
                          )}
                        </div>

                        {course.reasons && course.reasons.length > 0 && (
                          <div className="mb-3">
                            <p className="text-xs font-medium text-muted-foreground mb-1">
                              Why this course?
                            </p>
                            <ul className="text-xs text-muted-foreground list-disc list-inside">
                              {course.reasons.slice(0, 2).map((reason, idx) => (
                                <li key={idx}>{reason}</li>
                              ))}
                            </ul>
                          </div>
                        )}

                        <Button asChild className="w-full" variant="outline">
                          <a 
                            href={course.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="flex items-center justify-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            View Course
                          </a>
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </ScrollArea>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}