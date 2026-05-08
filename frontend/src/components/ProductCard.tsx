import React from 'react';
import { Product } from '../types';

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  return (
    <article className="product-card">
      <div className="product-card__body">
        <h4 className="product-card__title">{product.name}</h4>
        <div className="product-card__brand">{product.brand}</div>
        <div className="product-card__description">{product.description}</div>
        <div className="product-card__price-row">
          <span className="product-card__price">{product.price} ₽</span>
        </div>
        <div className="product-card__score">Совпадение: {product.match_score}%</div>
      </div>
    </article>
  );
};

export default ProductCard;
