import React, { useState, useEffect } from 'react';
import { food } from '../api';

function FoodPage() {
    const [recommendations, setRecommendations] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [form, setForm] = useState({ food_name: '', cost: '', calories: '', meal_type: 'lunch', is_homemade: false });
    const [success, setSuccess] = useState('');
    const [tab, setTab] = useState('log'); // 'log', 'recommendations', 'analysis'

    useEffect(() => { loadData(); }, []);

    async function loadData() {
        try {
            const [recs, budgetAnalysis] = await Promise.all([
                food.recommendations().catch(() => null),
                food.budgetAnalysis().catch(() => null)
            ]);
            setRecommendations(recs);
            setAnalysis(budgetAnalysis);
        } catch (err) {
            console.error(err);
        }
    }

    async function handleLogMeal(e) {
        e.preventDefault();
        setSuccess('');
        try {
            await food.log({
                ...form,
                cost: parseFloat(form.cost) || 0,
                calories: parseInt(form.calories) || 0
            });
            setSuccess('Meal logged!');
            setForm({ ...form, food_name: '', cost: '', calories: '' });
            loadData();
        } catch (err) {
            console.error(err);
        }
    }

    return (
        <div>
            <h1 style={{ marginBottom: '24px' }}>🍕 Food & Nutrition</h1>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                <button className={`btn ${tab === 'log' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('log')}>Log Meal</button>
                <button className={`btn ${tab === 'recommendations' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('recommendations')}>Recommendations</button>
                <button className={`btn ${tab === 'analysis' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setTab('analysis')}>Budget Analysis</button>
            </div>

            {/* Log Meal Tab */}
            {tab === 'log' && (
                <div className="card">
                    <div className="card-header"><h2>Log a Meal</h2></div>
                    {success && <div className="alert alert-success">{success}</div>}
                    <form onSubmit={handleLogMeal}>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="food-name">What did you eat?</label>
                                <input id="food-name" value={form.food_name}
                                    onChange={(e) => setForm({ ...form, food_name: e.target.value })}
                                    placeholder="e.g. Rice and beans" required />
                            </div>
                            <div className="form-group">
                                <label htmlFor="meal-type">Meal Type</label>
                                <select id="meal-type" value={form.meal_type}
                                    onChange={(e) => setForm({ ...form, meal_type: e.target.value })}>
                                    <option value="breakfast">Breakfast</option>
                                    <option value="lunch">Lunch</option>
                                    <option value="dinner">Dinner</option>
                                    <option value="snack">Snack</option>
                                </select>
                            </div>
                        </div>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="food-cost">Cost ($)</label>
                                <input id="food-cost" type="number" step="0.01" min="0" value={form.cost}
                                    onChange={(e) => setForm({ ...form, cost: e.target.value })}
                                    placeholder="5.00" />
                            </div>
                            <div className="form-group">
                                <label htmlFor="food-calories">Calories (optional)</label>
                                <input id="food-calories" type="number" min="0" value={form.calories}
                                    onChange={(e) => setForm({ ...form, calories: e.target.value })}
                                    placeholder="400" />
                            </div>
                        </div>
                        <div className="form-group">
                            <label>
                                <input type="checkbox" checked={form.is_homemade}
                                    onChange={(e) => setForm({ ...form, is_homemade: e.target.checked })} />
                                {' '}Homemade
                            </label>
                        </div>
                        <button type="submit" className="btn btn-primary">Log Meal</button>
                    </form>
                </div>
            )}

            {/* Recommendations Tab */}
            {tab === 'recommendations' && (
                <div>
                    {recommendations && (
                        <>
                            <div className="card">
                                <p style={{ fontSize: '0.95rem', marginBottom: '10px' }}>{recommendations.advice}</p>
                                {recommendations.savings_potential > 0 && (
                                    <div className="alert alert-info">
                                        💡 You could save ~${recommendations.savings_potential.toFixed(2)}/month by adjusting your food spending!
                                    </div>
                                )}
                            </div>
                            <div className="card">
                                <div className="card-header"><h2>Budget Meal Ideas</h2></div>
                                {recommendations.meals.map(meal => (
                                    <div className="meal-card" key={meal.id}>
                                        <h4>{meal.name}</h4>
                                        <div className="meal-meta">
                                            <span>💰 ${meal.cost.toFixed(2)}</span>
                                            <span>🔥 {meal.calories} cal</span>
                                            <span>⏱️ {meal.prep_time_minutes} min</span>
                                            {meal.is_vegetarian ? <span>🥬 Vegetarian</span> : null}
                                        </div>
                                        {meal.instructions && (
                                            <p style={{ fontSize: '0.85rem', color: 'var(--text-light)', marginTop: '8px' }}>
                                                {meal.instructions}
                                            </p>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </>
                    )}
                    {!recommendations && (
                        <div className="empty-state"><p>Log some meals first to get personalized recommendations!</p></div>
                    )}
                </div>
            )}

            {/* Budget Analysis Tab */}
            {tab === 'analysis' && analysis && (
                <div>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <div className="stat-value">${analysis.daily_average.toFixed(2)}</div>
                            <div className="stat-label">Daily food spend</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">${analysis.total_7_days.toFixed(2)}</div>
                            <div className="stat-label">Last 7 days total</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">${analysis.recommended_daily}</div>
                            <div className="stat-label">Recommended daily</div>
                        </div>
                    </div>
                    <div className="card">
                        <div className="card-header"><h2>Insight</h2></div>
                        <p>{analysis.tip}</p>
                    </div>
                    {analysis.by_meal_type?.length > 0 && (
                        <div className="card">
                            <div className="card-header"><h2>By Meal Type</h2></div>
                            <table>
                                <thead><tr><th>Meal</th><th>Avg Cost</th><th>Count</th></tr></thead>
                                <tbody>
                                    {analysis.by_meal_type.map(m => (
                                        <tr key={m.meal_type}>
                                            <td style={{ textTransform: 'capitalize' }}>{m.meal_type}</td>
                                            <td>${m.avg_cost?.toFixed(2)}</td>
                                            <td>{m.count}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default FoodPage;
