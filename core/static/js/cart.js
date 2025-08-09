<script>
    function addToCart(product_id) {
        console.log("Adding product to cart:", product_id);
    $.ajax({
        url: '{% url "cart:session-add-product" %}',  // match your path name exactly
    method: 'POST',
    data: {
        product_id: product_id,
    csrfmiddlewaretoken: '{{ csrf_token }}'
            },
    success: function (response) {
        console.log("Product added successfully:", response);
            },
    error: function (jqXHR, textStatus, errorThrown) {
        console.error("Error adding product:", textStatus, errorThrown);
            }
        });
    }
</script>
