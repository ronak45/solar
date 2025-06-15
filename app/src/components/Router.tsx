import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { PantryPage } from './pages/PantryPage';
import { RecipesPage } from './pages/RecipesPage';
import { CookingPage } from './pages/CookingPage';
import { SessionsPage } from './pages/SessionsPage';

export default function Router() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/pantry" element={<PantryPage />} />
      <Route path="/recipes" element={<RecipesPage />} />
      <Route path="/cooking/:sessionId" element={<CookingPage />} />
      <Route path="/sessions" element={<SessionsPage />} />
    </Routes>
  );
}