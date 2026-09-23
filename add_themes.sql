-- ============================================================
-- TuniWatch - Ajout des thèmes manquants et mots-clés
-- ============================================================

-- ============================================================
-- 1. THÈME : VIOLENCE CONTRE LES ENFANTS
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('violence_enfants', 'fr', 'violence infantile', 2.0),
('violence_enfants', 'fr', 'maltraitance enfant', 2.0),
('violence_enfants', 'fr', 'abus sexuel enfant', 2.0),
('violence_enfants', 'fr', 'pedophilie', 2.0),
('violence_enfants', 'fr', 'pédophilie', 2.0),
('violence_enfants', 'fr', 'enfant battu', 2.0),
('violence_enfants', 'fr', 'enfants battus', 2.0),
('violence_enfants', 'fr', 'exploitation enfant', 1.8),
('violence_enfants', 'fr', 'travail des enfants', 1.8),
('violence_enfants', 'fr', 'traite des enfants', 2.0),
('violence_enfants', 'fr', 'enlevement enfant', 1.8),
('violence_enfants', 'fr', 'enlèvement enfant', 1.8),
('violence_enfants', 'fr', 'violence sur mineur', 1.8),
-- Arabe
('violence_enfants', 'ar', 'عنف ضد الأطفال', 2.0),
('violence_enfants', 'ar', 'إساءة معاملة الأطفال', 2.0),
('violence_enfants', 'ar', 'تحرش بالأطفال', 2.0),
('violence_enfants', 'ar', 'اختطاف الأطفال', 2.0),
('violence_enfants', 'ar', 'تشغيل الأطفال', 1.8),
('violence_enfants', 'ar', 'الاتجار بالأطفال', 2.0),
('violence_enfants', 'ar', 'اغتصاب طفل', 2.0),
('violence_enfants', 'ar', 'ضرب الأطفال', 1.8),
('violence_enfants', 'ar', 'تعذيب الأطفال', 2.0);

-- ============================================================
-- 2. THÈME : APPELS À LA VIOLENCE
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('appels_violence', 'fr', 'appel a la violence', 2.0),
('appels_violence', 'fr', 'appel à la violence', 2.0),
('appels_violence', 'fr', 'incitation a la violence', 2.0),
('appels_violence', 'fr', 'incitation à la violence', 2.0),
('appels_violence', 'fr', 'provocation', 1.5),
('appels_violence', 'fr', 'terrorisme', 1.8),
('appels_violence', 'fr', 'terroriste', 1.8),
('appels_violence', 'fr', 'extremisme', 1.8),
('appels_violence', 'fr', 'extrémisme', 1.8),
('appels_violence', 'fr', 'extremiste', 1.8),
('appels_violence', 'fr', 'extrémiste', 1.8),
('appels_violence', 'fr', 'radicalisation', 1.8),
('appels_violence', 'fr', 'djihadisme', 1.8),
('appels_violence', 'fr', 'jihadisme', 1.8),
('appels_violence', 'fr', 'attentat', 1.8),
('appels_violence', 'fr', 'sabotage', 1.5),
-- Arabe
('appels_violence', 'ar', 'الدعوة إلى العنف', 2.0),
('appels_violence', 'ar', 'التحريض على العنف', 2.0),
('appels_violence', 'ar', 'الإرهاب', 2.0),
('appels_violence', 'ar', 'إرهابي', 2.0),
('appels_violence', 'ar', 'التطرف', 1.8),
('appels_violence', 'ar', 'متطرف', 1.8),
('appels_violence', 'ar', 'التطرف الديني', 1.8),
('appels_violence', 'ar', 'الجهاد', 1.5),
('appels_violence', 'ar', 'هجوم', 1.5),
('appels_violence', 'ar', 'اعتداء', 1.5);

-- ============================================================
-- 3. THÈME : PERSONNALITÉS POLITIQUES
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('personnalites_politiques', 'fr', 'kais saied', 2.0),
('personnalites_politiques', 'fr', 'kaïs saïed', 2.0),
('personnalites_politiques', 'fr', 'rached ghannouchi', 2.0),
('personnalites_politiques', 'fr', 'youssef chahed', 2.0),
('personnalites_politiques', 'fr', 'safi said', 2.0),
('personnalites_politiques', 'fr', 'safi saïd', 2.0),
('personnalites_politiques', 'fr', 'moustapha ferjani', 2.0),
('personnalites_politiques', 'fr', 'nabil karoui', 2.0),
('personnalites_politiques', 'fr', 'ahmed nejib chebbi', 1.8),
('personnalites_politiques', 'fr', 'moncef marzouki', 1.8),
('personnalites_politiques', 'fr', 'mehdi jomaa', 1.8),
('personnalites_politiques', 'fr', 'elyes fakhfakh', 1.8),
('personnalites_politiques', 'fr', 'hichem mechichi', 1.8),
('personnalites_politiques', 'fr', 'najla bouden', 1.8),
('personnalites_politiques', 'fr', 'ahmed hachani', 1.8),
('personnalites_politiques', 'fr', 'kamel madouri', 1.8),
('personnalites_politiques', 'fr', 'abir moussi', 1.8),
('personnalites_politiques', 'fr', 'samir dilou', 1.5),
-- Arabe
('personnalites_politiques', 'ar', 'قيس سعيد', 2.0),
('personnalites_politiques', 'ar', 'راشد الغنوشي', 2.0),
('personnalites_politiques', 'ar', 'يوسف الشاهد', 2.0),
('personnalites_politiques', 'ar', 'الصافي سعيد', 2.0),
('personnalites_politiques', 'ar', 'مصطفى الفرجاني', 2.0),
('personnalites_politiques', 'ar', 'نبيل القروي', 2.0),
('personnalites_politiques', 'ar', 'أحمد نجيب الشابي', 1.8),
('personnalites_politiques', 'ar', 'المنصف المرزوقي', 1.8),
('personnalites_politiques', 'ar', 'مهدي جمعة', 1.8),
('personnalites_politiques', 'ar', 'إلياس الفخفاخ', 1.8),
('personnalites_politiques', 'ar', 'هشام المشيشي', 1.8),
('personnalites_politiques', 'ar', 'نجلاء بودن', 1.8),
('personnalites_politiques', 'ar', 'أحمد الحشاني', 1.8),
('personnalites_politiques', 'ar', 'كمال المدوري', 1.8),
('personnalites_politiques', 'ar', 'عبير موسي', 1.8),
('personnalites_politiques', 'ar', 'سمير ديلو', 1.5);

-- ============================================================
-- 4. THÈME : MINORITÉS
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('minorites', 'fr', 'minorite', 1.8),
('minorites', 'fr', 'minorité', 1.8),
('minorites', 'fr', 'minorites religieuses', 2.0),
('minorites', 'fr', 'minorités religieuses', 2.0),
('minorites', 'fr', 'minorites sexuelles', 2.0),
('minorites', 'fr', 'minorités sexuelles', 2.0),
('minorites', 'fr', 'lgbtq', 2.0),
('minorites', 'fr', 'homosexuel', 1.8),
('minorites', 'fr', 'homosexuels', 1.8),
('minorites', 'fr', 'communaute juive', 1.8),
('minorites', 'fr', 'communauté juive', 1.8),
('minorites', 'fr', 'chretiens d orient', 1.8),
('minorites', 'fr', 'chrétiens d''orient', 1.8),
('minorites', 'fr', 'berberes', 1.8),
('minorites', 'fr', 'berbères', 1.8),
('minorites', 'fr', 'amazigh', 1.8),
('minorites', 'fr', 'amazighe', 1.8),
('minorites', 'fr', 'subsahariens', 1.5),
('minorites', 'fr', 'noirs de tunisie', 1.8),
-- Arabe
('minorites', 'ar', 'الأقليات', 2.0),
('minorites', 'ar', 'الأقليات الدينية', 2.0),
('minorites', 'ar', 'الأقليات الجنسية', 2.0),
('minorites', 'ar', 'المثليون', 2.0),
('minorites', 'ar', 'اليهود', 1.8),
('minorites', 'ar', 'المسيحيون', 1.8),
('minorites', 'ar', 'الأمازيغ', 1.8),
('minorites', 'ar', 'الأمازيغية', 1.8),
('minorites', 'ar', 'السود', 1.5),
('minorites', 'ar', 'الأفارقة', 1.5);

-- ============================================================
-- 5. THÈME : QUESTIONS RELIGIEUSES
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('questions_religieuses', 'fr', 'religion', 1.5),
('questions_religieuses', 'fr', 'religieux', 1.5),
('questions_religieuses', 'fr', 'religieuse', 1.5),
('questions_religieuses', 'fr', 'islam', 1.5),
('questions_religieuses', 'fr', 'islamique', 1.5),
('questions_religieuses', 'fr', 'islamiste', 1.8),
('questions_religieuses', 'fr', 'christianisme', 1.5),
('questions_religieuses', 'fr', 'judaisme', 1.5),
('questions_religieuses', 'fr', 'judaïsme', 1.5),
('questions_religieuses', 'fr', 'laicite', 1.8),
('questions_religieuses', 'fr', 'laïcité', 1.8),
('questions_religieuses', 'fr', 'secularisme', 1.8),
('questions_religieuses', 'fr', 'secularisme', 1.8),
('questions_religieuses', 'fr', 'hijab', 1.8),
('questions_religieuses', 'fr', 'voile', 1.5),
('questions_religieuses', 'fr', 'niqab', 1.8),
('questions_religieuses', 'fr', 'burqa', 1.8),
('questions_religieuses', 'fr', 'priere', 1.2),
('questions_religieuses', 'fr', 'prière', 1.2),
('questions_religieuses', 'fr', 'ramadan', 1.2),
('questions_religieuses', 'fr', 'mosquee', 1.5),
('questions_religieuses', 'fr', 'mosquée', 1.5),
('questions_religieuses', 'fr', 'eglise', 1.5),
('questions_religieuses', 'fr', 'église', 1.5),
('questions_religieuses', 'fr', 'synagogue', 1.5),
('questions_religieuses', 'fr', 'fatwa', 1.8),
('questions_religieuses', 'fr', 'charia', 1.8),
('questions_religieuses', 'fr', 'burkini', 1.8),
-- Arabe
('questions_religieuses', 'ar', 'الدين', 1.5),
('questions_religieuses', 'ar', 'الإسلام', 1.5),
('questions_religieuses', 'ar', 'الإسلامي', 1.5),
('questions_religieuses', 'ar', 'الإسلاميين', 1.8),
('questions_religieuses', 'ar', 'المسيحية', 1.5),
('questions_religieuses', 'ar', 'اليهودية', 1.5),
('questions_religieuses', 'ar', 'العلمانية', 1.8),
('questions_religieuses', 'ar', 'الحجاب', 1.8),
('questions_religieuses', 'ar', 'النقاب', 1.8),
('questions_religieuses', 'ar', 'الصلاة', 1.2),
('questions_religieuses', 'ar', 'رمضان', 1.2),
('questions_religieuses', 'ar', 'المسجد', 1.5),
('questions_religieuses', 'ar', 'الكنيسة', 1.5),
('questions_religieuses', 'ar', 'الفتوى', 1.8),
('questions_religieuses', 'ar', 'الشريعة', 1.8);

-- ============================================================
-- 6. THÈME : DISCRIMINATION RACIALE
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('discrimination_raciale', 'fr', 'racisme', 2.0),
('discrimination_raciale', 'fr', 'raciste', 2.0),
('discrimination_raciale', 'fr', 'racistes', 2.0),
('discrimination_raciale', 'fr', 'discrimination raciale', 2.0),
('discrimination_raciale', 'fr', 'segregation', 2.0),
('discrimination_raciale', 'fr', 'ségrégation', 2.0),
('discrimination_raciale', 'fr', 'apartheid', 2.0),
('discrimination_raciale', 'fr', 'esclavage', 1.8),
('discrimination_raciale', 'fr', 'xenophobie', 1.8),
('discrimination_raciale', 'fr', 'xénophobie', 1.8),
('discrimination_raciale', 'fr', 'propos racistes', 2.0),
('discrimination_raciale', 'fr', 'insulte raciale', 2.0),
('discrimination_raciale', 'fr', 'noir', 1.2),
('discrimination_raciale', 'fr', 'blanc', 1.2),
('discrimination_raciale', 'fr', 'africain', 1.3),
('discrimination_raciale', 'fr', 'subsaharien', 1.5),
-- Arabe
('discrimination_raciale', 'ar', 'التمييز العنصري', 2.0),
('discrimination_raciale', 'ar', 'العنصرية', 2.0),
('discrimination_raciale', 'ar', 'عنصري', 2.0),
('discrimination_raciale', 'ar', 'العبودية', 1.8),
('discrimination_raciale', 'ar', 'التفرقة العنصرية', 2.0),
('discrimination_raciale', 'ar', 'كراهية الأجانب', 1.8),
('discrimination_raciale', 'ar', 'السود', 1.5),
('discrimination_raciale', 'ar', 'البيض', 1.2),
('discrimination_raciale', 'ar', 'الأفارقة', 1.5);

-- ============================================================
-- 7. THÈME : DISCRIMINATION CONTRE LES FEMMES
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
-- Français
('discrimination_femmes', 'fr', 'discrimination femme', 2.0),
('discrimination_femmes', 'fr', 'discrimination femmes', 2.0),
('discrimination_femmes', 'fr', 'inegalite salariale', 2.0),
('discrimination_femmes', 'fr', 'inégalité salariale', 2.0),
('discrimination_femmes', 'fr', 'sexisme', 2.0),
('discrimination_femmes', 'fr', 'sexiste', 2.0),
('discrimination_femmes', 'fr', 'misogynie', 2.0),
('discrimination_femmes', 'fr', 'misogyne', 2.0),
('discrimination_femmes', 'fr', 'droits des femmes', 1.8),
('discrimination_femmes', 'fr', 'violence economique', 1.8),
('discrimination_femmes', 'fr', 'violence économique', 1.8),
('discrimination_femmes', 'fr', 'plafond de verre', 1.8),
('discrimination_femmes', 'fr', 'inegalite homme femme', 1.8),
('discrimination_femmes', 'fr', 'inégalité homme femme', 1.8),
('discrimination_femmes', 'fr', 'parite', 1.5),
('discrimination_femmes', 'fr', 'parité', 1.5),
-- Arabe
('discrimination_femmes', 'ar', 'التمييز ضد المرأة', 2.0),
('discrimination_femmes', 'ar', 'عدم المساواة', 1.8),
('discrimination_femmes', 'ar', 'التمييز الجنسي', 2.0),
('discrimination_femmes', 'ar', 'حقوق المرأة', 1.8),
('discrimination_femmes', 'ar', 'كره النساء', 2.0),
('discrimination_femmes', 'ar', 'التحيز ضد المرأة', 2.0);

-- ============================================================
-- 8. ÉLARGIR LE THÈME : ÉQUILIBRE POLITIQUE (avec personnalités)
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
('equilibre_politique', 'fr', 'kais saied', 1.5),
('equilibre_politique', 'fr', 'kaïs saïed', 1.5),
('equilibre_politique', 'fr', 'rached ghannouchi', 1.5),
('equilibre_politique', 'fr', 'youssef chahed', 1.5),
('equilibre_politique', 'fr', 'safi said', 1.5),
('equilibre_politique', 'fr', 'safi saïd', 1.5),
('equilibre_politique', 'fr', 'nabil karoui', 1.5),
('equilibre_politique', 'fr', 'abir moussi', 1.5),
('equilibre_politique', 'fr', 'ahmed nejib chebbi', 1.5),
('equilibre_politique', 'ar', 'قيس سعيد', 1.5),
('equilibre_politique', 'ar', 'راشد الغنوشي', 1.5),
('equilibre_politique', 'ar', 'يوسف الشاهد', 1.5),
('equilibre_politique', 'ar', 'الصافي سعيد', 1.5),
('equilibre_politique', 'ar', 'نبيل القروي', 1.5),
('equilibre_politique', 'ar', 'عبير موسي', 1.5),
('equilibre_politique', 'ar', 'أحمد نجيب الشابي', 1.5);

-- ============================================================
-- 9. ÉLARGIR : PRÉSENCE DES JEUNES
-- ============================================================
INSERT INTO mots_cles (theme, langue, mot, poids) VALUES
('presence_jeunes', 'fr', 'jeune', 1.5),
('presence_jeunes', 'fr', 'jeunes', 1.5),
('presence_jeunes', 'fr', 'jeunesse', 1.8),
('presence_jeunes', 'fr', 'etudiant', 1.5),
('presence_jeunes', 'fr', 'étudiant', 1.5),
('presence_jeunes', 'fr', 'etudiants', 1.5),
('presence_jeunes', 'fr', 'étudiants', 1.5),
('presence_jeunes', 'fr', 'diplome', 1.2),
('presence_jeunes', 'fr', 'diplômé', 1.2),
('presence_jeunes', 'ar', 'الشباب', 1.8),
('presence_jeunes', 'ar', 'شاب', 1.5),
('presence_jeunes', 'ar', 'شباب', 1.5),
('presence_jeunes', 'ar', 'طلاب', 1.5),
('presence_jeunes', 'ar', 'طالب', 1.5);

-- ============================================================
-- FIN
-- ============================================================
SELECT 'Thèmes et mots-clés ajoutés avec succès !' AS resultat;
SELECT theme, COUNT(*) AS nb_mots FROM mots_cles GROUP BY theme ORDER BY theme;