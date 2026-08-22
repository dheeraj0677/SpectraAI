export const DEMO_PRODUCTS = [
  {
    product_id: "PROD-DEMO-X500",
    product_name: {
      value: "UltraDrive X500 Industrial Inverter Motor",
      unit: null,
      confidence: 0.95,
      provenance: [
        {
          source_id: "pdf_sample",
          source_type: "datasheet_pdf",
          location: "Page 1, Header",
          extraction_method: "pdf-table-extractor",
          confidence: 0.95,
          raw_snippet: "UltraDrive X500 Industrial Inverter Motor - 480V 3-Phase",
          is_synthetic: false,
          raw_value: "UltraDrive X500 Industrial Inverter Motor",
          raw_unit: null,
          normalized_value: "UltraDrive X500 Industrial Inverter Motor",
          normalized_unit: null,
          normalization_rule: "Trimmed whitespace and standardized title casing"
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    manufacturer: {
      value: "Vortex Dynamics Tech",
      unit: null,
      confidence: 0.92,
      provenance: [
        {
          source_id: "image_sample",
          source_type: "nameplate_image",
          location: "Nameplate top left header",
          extraction_method: "claude-3-5-sonnet-vlm",
          confidence: 0.92,
          raw_snippet: "MFG: Vortex Dynamics Technologies Inc.",
          is_synthetic: false,
          raw_value: "Vortex Dynamics Technologies Inc.",
          raw_unit: null,
          normalized_value: "Vortex Dynamics Tech",
          normalized_unit: null,
          normalization_rule: "Mapped to standardized manufacturer directory"
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    model_number: {
      value: "VD-X500-480V-3P",
      unit: null,
      confidence: 0.96,
      provenance: [
        {
          source_id: "image_sample",
          source_type: "nameplate_image",
          location: "Model designation badge",
          extraction_method: "claude-3-5-sonnet-vlm",
          confidence: 0.96,
          raw_snippet: "MODEL: VD-X500-480V-3P",
          is_synthetic: false,
          raw_value: "VD-X500-480V-3P",
          raw_unit: null,
          normalized_value: "VD-X500-480V-3P",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    sku: {
      value: "SKU-VD-99201",
      unit: null,
      confidence: 0.9,
      provenance: [
        {
          source_id: "csv_sample",
          source_type: "erp_csv",
          location: "Row 1, Column SKU",
          extraction_method: "csv-schema-parser",
          confidence: 0.9,
          raw_snippet: "SKU: SKU-VD-99201",
          is_synthetic: false,
          raw_value: "SKU-VD-99201",
          raw_unit: null,
          normalized_value: "SKU-VD-99201",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    category: {
      value: "Industrial Motors & Drives",
      unit: null,
      confidence: 0.94,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "Taxonomy Classification DB",
          extraction_method: "taxonomy-classifier",
          confidence: 0.94,
          raw_snippet: "Classified to industrial power transmission category",
          is_synthetic: false,
          raw_value: "Industrial Motors & Drives",
          raw_unit: null,
          normalized_value: "Industrial Motors & Drives",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    description: {
      value: "The UltraDrive X500 is a high-performance 480V 3-Phase variable frequency drive designed for heavy industrial automation and precision motor control.",
      unit: null,
      confidence: 0.9,
      provenance: [
        {
          source_id: "pdf_sample",
          source_type: "datasheet_pdf",
          location: "Page 1, Executive Overview",
          extraction_method: "pdf-text-extractor",
          confidence: 0.9,
          raw_snippet: "High-performance VFD motor for heavy industrial automation applications.",
          is_synthetic: false,
          raw_value: "High-performance VFD motor for heavy industrial automation applications.",
          raw_unit: null,
          normalized_value: "The UltraDrive X500 is a high-performance 480V 3-Phase variable frequency drive designed for heavy industrial automation and precision motor control.",
          normalized_unit: null,
          normalization_rule: "Enriched with commercial clarity"
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    unspsc_code: {
      value: "26101100 - Electric Motors",
      unit: null,
      confidence: 0.9,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "UNSPSC v24.0 Taxonomy Mapping",
          extraction_method: "taxonomy-standardizer",
          confidence: 0.9,
          raw_snippet: "Mapped category 'Industrial Motors & Drives' to UNSPSC 26101100",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    etim_class: {
      value: "EC001851 (Electric Motor)",
      unit: null,
      confidence: 0.9,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "ETIM 9.0 International Standard",
          extraction_method: "etim-standardizer",
          confidence: 0.9,
          raw_snippet: "Mapped category 'Industrial Motors & Drives' to ETIM Class EC001851",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    commerce_readiness_score: 92.0,
    cri_breakdown: {
      identity_completeness: 25.0,
      specifications_depth: 25.0,
      taxonomy_compliance: 20.0,
      commerce_content: 15.0,
      quality_and_accuracy: 7.0
    },
    seo_title: {
      value: "Vortex Dynamics Tech UltraDrive X500 Industrial Inverter Motor 460V 15000W Model VD-X500-480V-3P",
      unit: null,
      confidence: 0.88,
      provenance: [
        {
          source_id: "unilog_content_generator",
          source_type: "rag_enrichment",
          location: "SEO Commerce Copy Engine",
          extraction_method: "seo-title-synthesis",
          confidence: 0.88,
          raw_snippet: "Synthesized commerce title: Vortex Dynamics Tech UltraDrive X500 Industrial Inverter Motor 460V 15000W Model VD-X500-480V-3P",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    interchangeable_parts: [
      {
        product_id: "prod_ref_101",
        product_name: "Ref-Drive X400",
        match_confidence: 85.0,
        reason: "Matches category 'Industrial Motors & Drives' and spec baseline (480V)."
      },
      {
        product_id: "prod_ref_102",
        product_name: "Ref-Drive X450",
        match_confidence: 85.0,
        reason: "Matches category 'Industrial Motors & Drives' and spec baseline (480V)."
      }
    ],
    specifications: {
      voltage: {
        value: "460V",
        unit: "V",
        confidence: 0.64,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 3, Electrical Characteristics",
            extraction_method: "pdf-table-extractor",
            confidence: 0.85,
            raw_snippet: "Rated Voltage: 480V AC 3-Phase 60Hz",
            is_synthetic: false,
            raw_value: "480V",
            raw_unit: "V",
            normalized_value: "480V",
            normalized_unit: "V",
            normalization_rule: "Standardized to Volt unit notation"
          },
          {
            source_id: "image_sample",
            source_type: "nameplate_image",
            location: "Nameplate electrical spec block",
            extraction_method: "claude-3-5-sonnet-vlm",
            confidence: 0.91,
            raw_snippet: "VOLTS: 460V 3PH",
            is_synthetic: false,
            raw_value: "460V",
            raw_unit: "V",
            normalized_value: "460V",
            normalized_unit: "V",
            normalization_rule: "Standardized to Volt unit notation"
          }
        ],
        status: "conflicted",
        conflict_candidates: [
          {
            value: "480V",
            unit: "V",
            confidence: 0.85,
            is_synthetic: false,
            observation_type: "directly_observed",
            provenance: [
              {
                source_id: "pdf_sample",
                source_type: "datasheet_pdf",
                location: "Page 3, Electrical Characteristics",
                extraction_method: "pdf-table-extractor",
                confidence: 0.85,
                raw_snippet: "Rated Voltage: 480V AC 3-Phase 60Hz",
                is_synthetic: false,
                raw_value: "480V",
                raw_unit: "V",
                normalized_value: "480V",
                normalized_unit: "V",
                normalization_rule: "Standardized to Volt unit notation"
              }
            ]
          },
          {
            value: "460V",
            unit: "V",
            confidence: 0.91,
            is_synthetic: false,
            observation_type: "directly_observed",
            provenance: [
              {
                source_id: "image_sample",
                source_type: "nameplate_image",
                location: "Nameplate electrical spec block",
                extraction_method: "claude-3-5-sonnet-vlm",
                confidence: 0.91,
                raw_snippet: "VOLTS: 460V 3PH",
                is_synthetic: false,
                raw_value: "460V",
                raw_unit: "V",
                normalized_value: "460V",
                normalized_unit: "V",
                normalization_rule: "Standardized to Volt unit notation"
              }
            ]
          }
        ],
        is_synthetic: false,
        observation_type: "conflicted"
      },
      power_watts: {
        value: "15000W",
        unit: "W",
        confidence: 0.93,
        provenance: [
          {
            source_id: "image_sample",
            source_type: "nameplate_image",
            location: "Nameplate rating box",
            extraction_method: "claude-3-5-sonnet-vlm",
            confidence: 0.93,
            raw_snippet: "RATING: 15 kW / 20 HP",
            is_synthetic: false,
            raw_value: "15000W",
            raw_unit: "W",
            normalized_value: "15000W",
            normalized_unit: "W",
            normalization_rule: "Standardized to Watt unit notation (15 kW -> 15000W)"
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      },
      weight_kg: {
        value: 48.5,
        unit: "kg",
        confidence: 0.89,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 12, Physical Specs Table",
            extraction_method: "pdf-table-extractor",
            confidence: 0.89,
            raw_snippet: "Net Weight: 48.5 kg (106.9 lbs)",
            is_synthetic: false,
            raw_value: 48.5,
            raw_unit: "kg",
            normalized_value: 48.5,
            normalized_unit: "kg",
            normalization_rule: "Standardized to kg notation"
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      },
      enclosure_rating: {
        value: "IP65",
        unit: null,
        confidence: 0.95,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 14, Environmental Specs",
            extraction_method: "pdf-text-extractor",
            confidence: 0.95,
            raw_snippet: "Enclosure Protection: Ingress Protection IP65",
            is_synthetic: false,
            raw_value: "IP65",
            raw_unit: null,
            normalized_value: "IP65",
            normalized_unit: null,
            normalization_rule: "Standardized IP rating code"
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      }
    },
    certifications: [
      {
        value: "CE, UL 508C, RoHS compliant, IP65 rated",
        unit: null,
        confidence: 0.94,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 14, Standards & Compliance",
            extraction_method: "pdf-text-extractor",
            confidence: 0.94,
            raw_snippet: "Certified UL 508C, CE marking, IP65 enclosure.",
            is_synthetic: false,
            raw_value: "CE, UL 508C, RoHS compliant, IP65 rated",
            raw_unit: null,
            normalized_value: "CE, UL 508C, RoHS compliant, IP65 rated",
            normalized_unit: null,
            normalization_rule: null
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      }
    ],
    warranty: {
      value: "24 Months Standard Warranty",
      unit: null,
      confidence: 0.75,
      provenance: [
        {
          source_id: "kb_seed_standards",
          source_type: "rag_enrichment",
          location: "unit_conventions.json",
          extraction_method: "rag-fill",
          confidence: 0.75,
          raw_snippet: "Standard manufacturer warranty for industrial grade equipment: 24 Months Limited",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    accessories: ["Braking Resistor Module", "Mounting Flange Kit", "Encoder Feedback Cable"],
    overall_confidence: 0.89,
    review_status: "needs_review",
    human_edits_log: [],
    consistency_warnings: []
  },
  {
    product_id: "PROD-OPT-920",
    product_name: {
      value: "OptiFlow Smart Optical Sensor",
      unit: null,
      confidence: 0.96,
      provenance: [
        {
          source_id: "pdf_sample",
          source_type: "datasheet_pdf",
          location: "Page 1, Header",
          extraction_method: "pdf-text-extractor",
          confidence: 0.96,
          raw_snippet: "OptiFlow-920 Precision Optical Flow Sensor",
          is_synthetic: false,
          raw_value: "OptiFlow-920 Precision Optical Flow Sensor",
          raw_unit: null,
          normalized_value: "OptiFlow Smart Optical Sensor",
          normalized_unit: null,
          normalization_rule: "Standardized product title"
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    manufacturer: {
      value: "SpectraPhotonics AG",
      unit: null,
      confidence: 0.94,
      provenance: [
        {
          source_id: "image_sample",
          source_type: "nameplate_image",
          location: "Label header",
          extraction_method: "claude-3-5-sonnet-vlm",
          confidence: 0.94,
          raw_snippet: "SpectraPhotonics AG - Switzerland",
          is_synthetic: false,
          raw_value: "SpectraPhotonics AG",
          raw_unit: null,
          normalized_value: "SpectraPhotonics AG",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    model_number: {
      value: "OF-920-IO-LINK",
      unit: null,
      confidence: 0.97,
      provenance: [
        {
          source_id: "image_sample",
          source_type: "nameplate_image",
          location: "Barcode panel",
          extraction_method: "claude-3-5-sonnet-vlm",
          confidence: 0.97,
          raw_snippet: "PN: OF-920-IO-LINK",
          is_synthetic: false,
          raw_value: "OF-920-IO-LINK",
          raw_unit: null,
          normalized_value: "OF-920-IO-LINK",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    sku: {
      value: "SKU-SP-4410",
      unit: null,
      confidence: 0.92,
      provenance: [
        {
          source_id: "csv_sample",
          source_type: "erp_csv",
          location: "Row 2, Column SKU",
          extraction_method: "csv-schema-parser",
          confidence: 0.92,
          raw_snippet: "SKU: SKU-SP-4410",
          is_synthetic: false,
          raw_value: "SKU-SP-4410",
          raw_unit: null,
          normalized_value: "SKU-SP-4410",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    category: {
      value: "Optical & Automation Sensors",
      unit: null,
      confidence: 0.95,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "Taxonomy Classification DB",
          extraction_method: "taxonomy-classifier",
          confidence: 0.95,
          raw_snippet: "Classified to industrial sensors & automation category",
          is_synthetic: false,
          raw_value: "Optical & Automation Sensors",
          raw_unit: null,
          normalized_value: "Optical & Automation Sensors",
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    description: {
      value: "High-speed laser-based optical flow sensor with integrated IO-Link interface for real-time velocity and presence tracking.",
      unit: null,
      confidence: 0.92,
      provenance: [
        {
          source_id: "pdf_sample",
          source_type: "datasheet_pdf",
          location: "Page 1, Abstract",
          extraction_method: "pdf-text-extractor",
          confidence: 0.92,
          raw_snippet: "High-speed laser optical sensor with IO-Link interface.",
          is_synthetic: false,
          raw_value: "High-speed laser optical sensor with IO-Link interface.",
          raw_unit: null,
          normalized_value: "High-speed laser-based optical flow sensor with integrated IO-Link interface for real-time velocity and presence tracking.",
          normalized_unit: null,
          normalization_rule: "Enriched for catalog presentation"
        }
      ],
      status: "extracted",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    unspsc_code: {
      value: "41111900 - Optical Instruments & Sensors",
      unit: null,
      confidence: 0.91,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "UNSPSC v24.0 Taxonomy Mapping",
          extraction_method: "taxonomy-standardizer",
          confidence: 0.91,
          raw_snippet: "Mapped category 'Optical & Automation Sensors' to UNSPSC 41111900",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    etim_class: {
      value: "EC002714 (Optical Sensor)",
      unit: null,
      confidence: 0.92,
      provenance: [
        {
          source_id: "unilog_taxonomy_engine",
          source_type: "rag_enrichment",
          location: "ETIM 9.0 International Standard",
          extraction_method: "etim-standardizer",
          confidence: 0.92,
          raw_snippet: "Mapped category 'Optical & Automation Sensors' to ETIM Class EC002714",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    commerce_readiness_score: 95.0,
    cri_breakdown: {
      identity_completeness: 25.0,
      specifications_depth: 25.0,
      taxonomy_compliance: 20.0,
      commerce_content: 15.0,
      quality_and_accuracy: 10.0
    },
    seo_title: {
      value: "SpectraPhotonics AG OptiFlow Smart Optical Sensor IO-Link 24V DC Model OF-920-IO-LINK",
      unit: null,
      confidence: 0.93,
      provenance: [
        {
          source_id: "unilog_content_generator",
          source_type: "rag_enrichment",
          location: "SEO Commerce Copy Engine",
          extraction_method: "seo-title-synthesis",
          confidence: 0.93,
          raw_snippet: "Synthesized commerce title: SpectraPhotonics AG OptiFlow Smart Optical Sensor IO-Link 24V DC Model OF-920-IO-LINK",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    interchangeable_parts: [],
    specifications: {
      supply_voltage: {
        value: "24V DC",
        unit: "V",
        confidence: 0.96,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 2, Electrical Ratings",
            extraction_method: "pdf-table-extractor",
            confidence: 0.96,
            raw_snippet: "Operating Voltage: 18-30V DC (Nominal 24V DC)",
            is_synthetic: false,
            raw_value: "24V DC",
            raw_unit: "V",
            normalized_value: "24V DC",
            normalized_unit: "V",
            normalization_rule: "Standardized to DC nominal notation"
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      },
      sensing_range: {
        value: "500mm",
        unit: "mm",
        confidence: 0.94,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 3, Optical Parameters",
            extraction_method: "pdf-table-extractor",
            confidence: 0.94,
            raw_snippet: "Max Working Distance: 500 mm",
            is_synthetic: false,
            raw_value: "500mm",
            raw_unit: "mm",
            normalized_value: "500mm",
            normalized_unit: "mm",
            normalization_rule: "Standardized metric length"
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      },
      interface: {
        value: "IO-Link v1.1 / PNP / NPN",
        unit: null,
        confidence: 0.95,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 4, Output Configuration",
            extraction_method: "pdf-text-extractor",
            confidence: 0.95,
            raw_snippet: "Communication: IO-Link v1.1 COM3, configurable push-pull output.",
            is_synthetic: false,
            raw_value: "IO-Link v1.1 / PNP / NPN",
            raw_unit: null,
            normalized_value: "IO-Link v1.1 / PNP / NPN",
            normalized_unit: null,
            normalization_rule: null
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      }
    },
    certifications: [
      {
        value: "CE, cULus Listed, IP67, Ecolab",
        unit: null,
        confidence: 0.96,
        provenance: [
          {
            source_id: "pdf_sample",
            source_type: "datasheet_pdf",
            location: "Page 6, Compliance",
            extraction_method: "pdf-text-extractor",
            confidence: 0.96,
            raw_snippet: "Approvals: CE, cULus, IP67, Ecolab certified enclosure.",
            is_synthetic: false,
            raw_value: "CE, cULus Listed, IP67, Ecolab",
            raw_unit: null,
            normalized_value: "CE, cULus Listed, IP67, Ecolab",
            normalized_unit: null,
            normalization_rule: null
          }
        ],
        status: "extracted",
        conflict_candidates: null,
        is_synthetic: false,
        observation_type: "directly_observed"
      }
    ],
    warranty: {
      value: "36 Months Manufacturer Warranty",
      unit: null,
      confidence: 0.9,
      provenance: [
        {
          source_id: "kb_seed_standards",
          source_type: "rag_enrichment",
          location: "unit_conventions.json",
          extraction_method: "rag-fill",
          confidence: 0.9,
          raw_snippet: "Sensor electronics standard warranty: 36 Months",
          is_synthetic: false,
          raw_value: null,
          raw_unit: null,
          normalized_value: null,
          normalized_unit: null,
          normalization_rule: null
        }
      ],
      status: "enriched",
      conflict_candidates: null,
      is_synthetic: false,
      observation_type: "directly_observed"
    },
    accessories: ["M12 4-Pin Shielded Cable", "Precision Bracket Kit", "Optical Reflector Target"],
    overall_confidence: 0.95,
    review_status: "approved",
    human_edits_log: [],
    consistency_warnings: []
  }
];

export const DEMO_GRAPH = {
  nodes: [
    { id: "cat_motors", label: "Industrial Motors & Drives", type: "category" },
    { id: "cat_sensors", label: "Optical & Automation Sensors", type: "category" },
    { id: "PROD-DEMO-X500", label: "UltraDrive X500 (Vortex)", type: "product" },
    { id: "PROD-OPT-920", label: "OptiFlow Smart Sensor", type: "product" },
    { id: "prod_ref_101", label: "Ref-Drive X400", type: "product" },
    { id: "prod_ref_102", label: "Ref-Drive X450", type: "product" },
    { id: "acc_resistor", label: "Braking Resistor Module", type: "accessory" },
    { id: "acc_flange", label: "Mounting Flange Kit", type: "accessory" },
    { id: "acc_m12", label: "M12 4-Pin Cable", type: "accessory" }
  ],
  links: [
    { source: "PROD-DEMO-X500", target: "cat_motors", relation: "belongs_to_category" },
    { source: "PROD-OPT-920", target: "cat_sensors", relation: "belongs_to_category" },
    { source: "PROD-DEMO-X500", target: "prod_ref_101", relation: "interchangeable_with" },
    { source: "PROD-DEMO-X500", target: "prod_ref_102", relation: "interchangeable_with" },
    { source: "PROD-DEMO-X500", target: "acc_resistor", relation: "has_accessory" },
    { source: "PROD-DEMO-X500", target: "acc_flange", relation: "has_accessory" },
    { source: "PROD-OPT-920", target: "acc_m12", relation: "has_accessory" }
  ]
};
