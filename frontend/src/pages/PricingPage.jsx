// src/pages/PricingPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPricingRules, createPricingRule, deletePricingRule } from '../services/api';
import Navbar from '../components/Navbar';

function PricingPage() {
    const { resourceId } = useParams();
    const [rules, setRules] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // Form state
    const [basePrice, setBasePrice] = useState('');
    const [durationType, setDurationType] = useState('PER_HOUR');
    const [minDuration, setMinDuration] = useState('');
    const [maxDuration, setMaxDuration] = useState('');
    const [name, setName] = useState('');

    const loadRules = async () => {
        setIsLoading(true);
        try {
            const data = await getPricingRules(resourceId);
            setRules(data);
        } catch (error) {
            alert(error.message);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        loadRules();
    }, [resourceId]);

    const handleDelete = async (ruleId) => {
        if (!window.confirm('Bu fiyatlandırma kuralını silmek istediğinize emin misiniz?')) return;
        try {
            await deletePricingRule(resourceId, ruleId);
            setRules(rules.filter(r => r.price_rule_id !== ruleId));
            alert('Kural silindi.');
        } catch (error) {
            alert(error.message);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const newRule = {
            base_price: parseFloat(basePrice),
            duration_type: durationType,
            min_duration: minDuration ? parseInt(minDuration) : null,
            max_duration: maxDuration ? parseInt(maxDuration) : null,
            name: name || null,
            currency: 'TRY'
        };

        try {
            const createdRule = await createPricingRule(resourceId, newRule);
            setRules([...rules, createdRule]);
            alert('Fiyatlandırma kuralı başarıyla eklendi.');
            // Formu sıfırla
            setBasePrice('');
            setName('');
            setMinDuration('');
            setMaxDuration('');
        } catch (error) {
            alert(`Hata: ${error.message}`);
        }
    };

    if (isLoading) return <p className="text-center p-10">Yükleniyor...</p>;

    return (
        <>
            <Navbar />
            <div className="container mx-auto p-8">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-3xl font-bold">Fiyatlandırma Yönetimi</h1>
                    <Link to="/dashboard/resources" className="text-blue-500 hover:underline">
                        &larr; Varlık Listesine Dön
                    </Link>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    {/* Liste */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h2 className="text-2xl font-semibold mb-4">Mevcut Fiyat Kuralları</h2>
                        {rules.length > 0 ? (
                            <ul className="divide-y divide-gray-200">
                                {rules.map(rule => (
                                    <li key={rule.price_rule_id} className="py-4 flex justify-between items-center">
                                        <div>
                                            <p className="font-bold text-lg">{rule.base_price} {rule.currency} / {rule.duration_type}</p>
                                            {rule.name && <p className="text-sm text-gray-500">{rule.name}</p>}
                                            <p className="text-xs text-gray-400">
                                                Min: {rule.min_duration || '-'} dk | Max: {rule.max_duration || '-'} dk
                                            </p>
                                        </div>
                                        <button onClick={() => handleDelete(rule.price_rule_id)} className="text-red-500 hover:text-red-700">
                                            Sil
                                        </button>
                                    </li>
                                ))}
                            </ul>
                        ) : (
                            <p className="text-gray-500 italic">Henüz bir fiyat kuralı eklenmemiş.</p>
                        )}
                    </div>

                    {/* Form */}
                    <div className="bg-white p-6 rounded-lg shadow-md">
                        <h2 className="text-2xl font-semibold mb-4">Yeni Kural Ekle</h2>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div>
                                <label className="block text-gray-700 font-bold mb-1">Kural Adı (İsteğe Bağlı)</label>
                                <input type="text" value={name} onChange={e => setName(e.target.value)} className="w-full p-2 border rounded" placeholder="Örn: Standart Fiyat" />
                            </div>

                            <div>
                                <label className="block text-gray-700 font-bold mb-1">Birim Fiyat (TL)</label>
                                <input type="number" step="0.01" value={basePrice} onChange={e => setBasePrice(e.target.value)} className="w-full p-2 border rounded" required />
                            </div>

                            <div>
                                <label className="block text-gray-700 font-bold mb-1">Ücretlendirme Tipi</label>
                                <select value={durationType} onChange={e => setDurationType(e.target.value)} className="w-full p-2 border rounded">
                                    <option value="PER_HOUR">Saatlik (PER_HOUR)</option>
                                    <option value="PER_DAY">Günlük (PER_DAY)</option>
                                    <option value="FIXED_PRICE">Sabit (FIXED_PRICE)</option>
                                    <option value="PER_MINUTE">Dakikalık (PER_MINUTE)</option>
                                </select>
                            </div>

                            <div className="flex space-x-4">
                                <div className="w-1/2">
                                    <label className="block text-gray-700 font-bold mb-1">Min Süre (Dk)</label>
                                    <input type="number" value={minDuration} onChange={e => setMinDuration(e.target.value)} className="w-full p-2 border rounded" placeholder="Opsiyonel" />
                                </div>
                                <div className="w-1/2">
                                    <label className="block text-gray-700 font-bold mb-1">Max Süre (Dk)</label>
                                    <input type="number" value={maxDuration} onChange={e => setMaxDuration(e.target.value)} className="w-full p-2 border rounded" placeholder="Opsiyonel" />
                                </div>
                            </div>

                            <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mt-4">
                                Kuralı Ekle
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </>
    );
}

export default PricingPage;
